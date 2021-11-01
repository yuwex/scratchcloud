import asyncio
import requests
import websockets
import json
import aiohttp
import time

from websockets.exceptions import ConnectionClosedError

class CloudChange:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value
        
    def __repr__(self):
        return f'<CloudChange: name={self.name}, value={self.value}>'

class CloudClient:
    def __init__(self, username: str, project_id: str, max_reconnect = None, reconnect_cooldown = 10, encoder = None, decoder = None):

        self.username = username
        self.project_id = project_id
        self.loop = asyncio.get_event_loop()
        self.http_session = None
        self.cookies = None
        self.headers = None
        self.logged_in = False
        self.ws = None
        self.connected = False
        self.max_reconnect = max_reconnect
        self.reconnect_cooldown = reconnect_cooldown

        self.decoder = decoder
        self.encoder = encoder

        self.cloud_variables = {}

        self.commands = []
        self.cloud_events = {}
        self.cloud_event_errors = {}

    # RUNNING CLIENT
    def run(self, token: str):
        loop = self.loop

        restart = False
        reconnects = 0

        while True:
            try:
                # Run Main loop
                loop.run_until_complete(self.start(token))
            except KeyboardInterrupt:
                # Stop Loop if KeyboardInterrupt
                loop.create_task(self.on_disconnect_task())
                loop.run_until_complete(self.close())
                break
            except (ConnectionClosedError, ConnectionError, requests.exceptions.ConnectionError) as e:
                print(e)
                # If connection closed, reconnect

                loop.create_task(self.on_disconnect_task())
                loop.run_until_complete(self.close())
                time.sleep(self.reconnect_cooldown)

                if self.connected:
                    restart = True
                    reconnects = 0
                else:
                    reconnects += 1

                # Don't reconnect if first time
                if not restart:
                    raise e
                
                if reconnects == self.max_reconnect:
                    print(f'Reconnection failed {reconnects} times. Stopping...')
                    raise e
            except Exception as e:
                print(f'Uncaught Exception with type: {e}')
                raise e

    async def start(self, token: str):
        self.connected = False
        await self.close()
        
        await self.login(token)
        await self.connect_ws()
        await self.ws_handshake()
        
        self.connected = True
        await self.run_tasks()

    async def run_tasks(self):
        await asyncio.gather(self.on_connect_task(), self.on_recv())

    async def close(self):
        if self.http_session:
            await self.http_session.close()

    async def ws_send(self, data: dict):
        data = json.dumps(data) + '\n'
        await self.ws.send(data)

    # START REQS
    async def login(self, token: str) -> None:
    
        headers = {
            "X-CSRFToken": "None",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://scratch.mit.edu",
            "User-Agent": "None"
        }
        
        session = requests.Session()
        
        with session.get("https://scratch.mit.edu/csrf_token/", headers=headers) as r:
            csrf = r.cookies['scratchcsrftoken']
        
        headers['X-CSRFToken'] = csrf

        data = {
            'username': self.username,
            'password': token
        }

        with session.post("https://scratch.mit.edu/login/", data=json.dumps(data), headers=headers) as p:
            assert p.status_code == 200, 'Login Error: Not 200 login status!'

        cookies = session.cookies.get_dict()

        self.http_session = aiohttp.ClientSession(cookies=cookies, headers=headers)
        self.cookies = cookies
        self.headers = headers
        self.logged_in = True

    async def connect_ws(self):

        def dict_to_cookie(dictionary: dict) -> str:
            if dictionary:
                return '; '.join([f'{key}={val}' for key, val in dictionary.items()]) + ';'

        cookie = {'Cookie': dict_to_cookie(self.cookies)}
        self.ws = await websockets.connect('wss://clouddata.scratch.mit.edu', origin='https://scratch.mit.edu', extra_headers=cookie)

    async def ws_handshake(self):
        payload = {
            'method': 'handshake',
            'user': self.username,
            'project_id': self.project_id
        }
        await self.ws_send(payload)

        data = await asyncio.wait_for(self.ws.recv(), 5)
        self.cloud_variables.update(self.parse_raw_cloud(data))

    # TASKS
    async def on_recv(self):
        async for data in self.ws:
            for name, value in self.parse_raw_cloud(data).items():
                
                self.cloud_variables.update({name: value})
                cloud = CloudChange(name, value)

                for func_name, cloud_event_name in self.cloud_events.items():
                    if cloud_event_name == name:
                        
                        try:
                            if self.decoder:
                                cloud.value = self.decoder(value)
                            await getattr(self, f'{func_name}')(cloud)
                        except Exception as e:
                            if name in self.cloud_event_errors.keys():
                                await getattr(self, f'{self.cloud_event_errors[name]}')(cloud, e)
                            else:
                                raise e
                
                               
                await self.on_message(cloud)
                  
    async def on_connect_task(self):
        await self.on_connect()

    async def on_disconnect_task(self):
        await self.on_disconnect()

    # EVENTS
    def event(self, func):
        f_name = func.__name__
        
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)

        if f_name == 'on_message':
            setattr(self, 'on_message', func)
            return wrap
        
        elif f_name == 'on_connect':
            setattr(self, 'on_connect', func)
            return wrap
        
        elif f_name == 'on_disconnect':
            setattr(self, 'on_disconnect', func)
            return wrap

    def cloud_event(self, variable_name: str):
        def decorator(func):
            f_name = func.__name__
            c_name = f'_cloud_event_{f_name}'

            def wrap(*args, **kwargs):
                return func(*args, **kwargs)

            if c_name in self.cloud_events.keys():
                raise TypeError(f'cloud_event function with name {f_name} already exists.')
        
            self.cloud_events.update({c_name: variable_name})
            setattr(self, c_name, func)

            return wrap
        return decorator

    def cloud_event_error(self, variable_name: str):
        def decorator(func):
            f_name = func.__name__
            c_name = f'_cloud_event_error_{f_name}'

            def wrap(*args, **kwargs):
                return func(*args, **kwargs)

            if c_name in self.cloud_events.values():
                raise TypeError(f'cloud_event_error for cloud variable {variable_name} already exists.')
        
            self.cloud_event_errors.update({variable_name: c_name})
            setattr(self, c_name, func)

            return wrap
        return decorator

    async def on_message(self, content):
        pass

    async def on_connect(self):
        pass

    async def on_disconnect(self):
        pass

    ### CLOUD VARIABLES
    async def set_cloud(self, name: str, value: str):
        
        value = str(value)

        if self.encoder:
            value = self.encoder(value)
        
        assert value.isdigit(), 'Cloud value must be digits'

        assert len(value) <= 256, 'Cloud value length must be under or equal to 256 digits.'
        
        payload = {
            'method': 'set',
            'name': f'☁ {name}',
            'value': value,
            'user': self.username,
            'project_id': self.project_id,
        }

        await self.ws_send(payload)

    def parse_raw_cloud(self, raw_data: str) -> dict:

        parsed_data = {}

        data_set = raw_data.split('\n')[:-1]
        for data in data_set:
            try:
                data = json.loads(data)
            except:
                continue

            name = data['name'][2:]
            value = data['value']
            parsed_data.update({name: value})
        
        return parsed_data