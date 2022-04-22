from __future__ import annotations

import asyncio
import json
import time
from typing import Callable

import websockets
from websockets.exceptions import ConnectionClosedError
import aiohttp

from .errors import SizeError, MissingCloudVariable

class LoginCookie:
    """This is a class that stores login cookie data. It is used by `client.CloudClient`.

    :param csrftoken: the user's CSRFToken.
    :type csrftoken: str
    :param sessionid: the user's ScratchSessionID.
    :type sessionid: str

    What is this?

    Scratch occasionally blocks new logins from online IDEs. This is most common with the popular IDE, Repl.it. When logging in to scratch normally, Scratch creates a "Session ID" and "CSRF Token" and uses them for your cridentials. You can insert these cridentials directly to scratchcloud to bypass the login process. Anyone with these cridentials can do anything on your account, so make sure to keep them safe!

    The LoginCookie object can be used in place of a password for the :meth:`client.CloudClient.run` method.

    Cookie Example Usage::
        from scratchcloud import CloudClient, LoginCookie

        login_cookie = LoginCookie(
            csrftoken = 'abc123',
            sessionid = 'def456'
        )

        client = CloudClient('username', '123')
        # more code here
        client.run(login_cookie)
    """

    def __init__(self, csrftoken: str, sessionid: str):
        self.csrftoken = csrftoken
        self.sessionid = sessionid

    def to_cookie_dict(self) -> dict:
        """A method that returns the cookie dictionary in a format that scratch likes.

        :rtype: dict
        """

        return {
            'scratchcsrftoken': self.csrftoken,
            'scratchsessionsid': self.sessionid
        }

class CloudChange:
    """This is a class that stores cloud data received from :class:`client.CloudClient`.
    
    :param name: the cloud variable's name excluding `"☁️ "`.
    :type name: str
    :param value: the cloud variable's value.
        If an decoder is specified in :class:`client.CloudClient` this value will be decoded.
    :type value: str
    :param id: the library-assigned cloud variable's id. This value will start at 1 for the first cloud variable received and increment for each new change.
    :type id: int
    :param previous_value: the cloud variable's previous value.
        Never encoded. None if not found.
    :type previous_value: str, optional
    :param sender: the cloud variable's sender.
        If sent from the client, will be the :class:`client.CloudClient` object. None otherwise. This value may be changed by extensions.
    :type sender: :class:`client.CloudClient` | str
    """

    def __init__(self, name: str, value: str, id: int, previous_value: str = None, sender: 'CloudClient' | str = None):
        self.name = name
        self.value = value
        self.id = id

        self.previous_value = previous_value
        self.received_at: float = time.time()
        self.sender = sender
        self.decoded = False

    def __gt__(self, other):
        if not isinstance(other, CloudChange):
            raise TypeError(f'CloudChange cannot be compared to type {type(other)}')
        
        return self.received_at > other.received_at
    
    def __lt__(self, other):
        if not isinstance(other, CloudChange):
            raise TypeError(f'CloudChange cannot be compared to type {type(other)}')
        
        return self.received_at < other.received_at

    def __repr__(self):
        return f'<{type(self)}: name={self.name}, value={self.value}, id={self.id}, previous_value={self.previous_value}, received_at={self.received_at}, sender={self.sender}>'

class RawCloudChange(CloudChange):
    """A subclass of :class:`client.CloudChange`.
    Value attribute wil never be encoded. Used in `client.cloud_cache`
    """

    pass

class CloudClient:
    """Represents the connection with the scratch websocket server.

    :param username: the username of the account that will connect to scratch.
    :type username: str
    :param project_id: the project id that will be connected to. 
    :type project_id: str
    :param max_reconnect: the maximum number of reconnects by the client. If reconnecting fails this number of times, the error that caused the reconnect will be raised. Defaults to None, which means always reconnect.
    :type max_reconnect: int, optional
    :param reconnect_cooldown: the time in seconds between reconnecting. Defaults to 10. Low values may result in account ratelimiting and bans.
    :type reconnect_cooldown: int, optional
    :param encoder: a callable function that is used to encode all sent cloud data.
        The function must return a string of digits and take 1 argument.
    :type encoder: Callable[[str], str], optional
    :param decoder: a callable function that is used to decode all received cloud data.
        The function must take 1 argument.
    :type decoder: Callable[[str], str], optional
    :param disconnect_messages: a boolean that when true, prints the cause of disconnects. 
        defaults to False
    :type disconnect_messages: bool
    :param max_cache_length: the maximum length of saved RawCloudChange objects.
        defaults to 1000
    :type max_cache_length: int
    :param event_loop: the event loop that the CloudClient will use.
        defaults to asyncio.get_event_loop()
    :type event_loop: AbstractEventLoop

    **Attributes:**
    
    * http_session :class:`aiohttp.ClientSession`
        The HTTP session used for logging into scratch
    * cookies :class:`dict`
        The cookies gathered from the HTTP session
    * headers :class:`dict`
        The headers gathered from the HTTP session
    * logged_in :class:`bool`
        If client is logged in
    * ws :class:`websockets.client`
        The websocket connection
    * connected :class:`bool`
        If the client is connected to the websocket server
    * cloud_variables :class:`dict`
        The current values of the cloud variables
    * cloud_cache :class:`list[RawCloudChange]`
        A list of all of the cloud variable changed since the client has been active. Newer cloud changes will be later in the list
    * cloud_events :class:`dict`
        Internal registers for cloud events
    * cloud_event_errors :class:`dict`
        Internal registers for cloud event errors
    * on_message_registered :class:`bool`
        If the on_messsage event is registered
    
    **Methods:**
    """

    def __init__(self, username: str, project_id: str, max_reconnect: int = None, reconnect_cooldown: int = 10, encoder: Callable[[str], str] = None, decoder: Callable[[str], str] = None, disconnect_messages: bool = False, max_cache_length: int = 1000, event_loop = asyncio.get_event_loop()):

        self.username = username
        self.project_id = project_id

        self.loop = event_loop

        self.http_session = None
        self.cookies = None
        self.headers = None
        self.logged_in = False
        self.ws = None
        self.connected = False

        self.max_reconnect = max_reconnect
        self.reconnect_cooldown = reconnect_cooldown
        self.disconnect_messages = disconnect_messages

        self.decoder = decoder
        self.encoder = encoder

        self.cloud_variables = {}
        self.cloud_cache = []
        self.max_cache_length = max_cache_length

        self.cloud_events = {}
        self.cloud_event_errors = {}

        self.on_message_registered = False

    # RUNNING CLIENT
    def run(self, token: str | LoginCookie):
        """A blocking function to run the client with library reconnecting.
        Basically runs start repeatedly and disconnects properly after a KeyboardInterrupt.
        Also handles common connection errors.

        :param token: the password or a LoginCookie object for the account that will be used to establish a connection

        :rtype: None

        Example Usage::

            client = CloudClient('username', '123')
            client.run('password')
        
        Cookie Example Usage::

            login_cookie = LoginCookie(
                csrftoken = 'abc123',
                sessionid = 'def456'
            )

            client = CloudClient('username', '123')
            client.run(login_cookie)
        """

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
            except (ConnectionClosedError, ConnectionError, TimeoutError) as e:
                self.logged_in = False
                if self.disconnect_messages:
                    print(f'Disconnected due to type: {type(e)}\n{e}')
                
                # If previously connected, run disconnect task and reconnect again.
                if self.connected:
                    restart = True
                    reconnects = 0
                else:
                    reconnects += 1

                # If previously connected, run disconnect task
                if restart:
                    loop.create_task(self.on_disconnect_task())

                # Close everything :)
                loop.run_until_complete(self.close())

                # If never previously connected, raise error.
                if not restart:
                    raise e
                
                time.sleep(self.reconnect_cooldown)
                
                if reconnects == self.max_reconnect:
                    print(f'Reconnection failed {reconnects} times. Stopping...')
                    raise e
            except Exception as e:
                print(f'ScratchCloud got uncaught Exception with type: {e}')
                raise e

    async def start(self, token: str | LoginCookie):
        """A coroutine that starts a client.

        Calls all functions needed to connect to scratch in chronological order.
        Closes self, logs in, connects to the websocket, performs a handshake, and finally, runs the client.

        This can be used in place of :meth:`run` if you want more control over the event loop.

        :param token: the password of the account that will be used to establish a connection
        :type token: str
        :param token: the cookie for the account that will be used to establish a connection.
        :type token: LoginCookie

        Internal.
        """

        self.connected = False
        await self.close()

        await self.login(token)
        await self.connect_ws()
        await self.ws_handshake()
        
        self.connected = True
        await self.run_client()


    async def run_client(self):
        """A coroutine that calls the on_connect_task and starts receving data from the websocket.
        Assumes that the websocket connection has already been established.

        Internal.
        """

        await asyncio.gather(self.on_connect_task(), self.on_recv())

    async def close(self):
        """A coroutine that closes self.http_session.

        Internal.
        """

        if self.http_session:
            await self.http_session.close()

    async def ws_send(self, data: dict):
        """A coroutine that sends a dictionary to the websocket connection.
        Assumes that the websocket connection has already been established.

        Internal.
        """

        data = json.dumps(data) + '\n'
        return await self.ws.send(data)

    # START REQS
    async def login(self, token: str | LoginCookie) -> None:
        """A coroutine that sets http_session, cookies, and headers.
        
        :param token: the password of the account that will be used to establish a connection
        :type token: str 

        Internal.
        """

        headers = {
            "X-CSRFToken": "None",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://scratch.mit.edu",
            "User-Agent": "scratchcloud"
        }
        
        cookies = {}

        if isinstance(token, LoginCookie):
            headers['X-CSRFToken'] = token.csrftoken
            cookies = token.to_cookie_dict()
        else:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get('https://scratch.mit.edu/csrf_token/'):
                    filtered = session.cookie_jar.filter_cookies('https://scratch.mit.edu')
                    csrf = filtered['scratchcsrftoken'].value

                    headers['X-CSRFToken'] = csrf
                    cookies['scratchcsrftoken'] = csrf

                data = {
                    'username': self.username,
                    'password': token,
                }

                async with session.post('https://scratch.mit.edu/login/', data=json.dumps(data), headers=headers) as p:
                    if p.status != 200:
                        raise ConnectionError(f'Login Error: Not 200 login status! Got {p.status}')

                    filtered = session.cookie_jar.filter_cookies('https://scratch.mit.edu')

                    cookies['scratchsessionsid'] = filtered['scratchsessionsid'].value

        self.http_session = aiohttp.ClientSession(cookies=cookies, headers=headers)
        self.cookies = cookies
        self.headers = headers
        self.logged_in = True

    async def connect_ws(self):
        """A coroutine that establishes a websocket connection with project_id.
        Assumes that the http session has already been created.

        Internal.
        """

        def dict_to_cookie(dictionary: dict) -> str:
            if dictionary:
                return '; '.join([f'{key}={val}' for key, val in dictionary.items()]) + ';'

        cookie = {'Cookie': dict_to_cookie(self.cookies)}
        self.ws = await websockets.connect('wss://clouddata.scratch.mit.edu', origin='https://scratch.mit.edu', extra_headers=cookie)

    async def ws_handshake(self):
        """A coroutine that performs a handshake with the websocket connection.
        
        :raises `errors.MissingCloudVariable`: If no cloud variables are found in the project

        Internal.
        """

        payload = {
            'method': 'handshake',
            'user': self.username,
            'project_id': self.project_id
        }
        await self.ws_send(payload)
        
        try:
            data = await asyncio.wait_for(self.ws.recv(), 5)
        except:
            await self.close()
            raise MissingCloudVariable('No Cloud Variables Found!')
        self.cloud_variables.update(self.parse_raw_cloud(data))

    # TASKS
    async def on_recv(self):
        """A coroutine that receives data from the cloud connection and calls event functions.
        Creates CloudChange objects, manages the cache, and handles events and cloud_events.

        Internal.
        """

        async for data in self.ws:
            for name, value in self.parse_raw_cloud(data).items():
                
                if name in self.cloud_variables:
                    prev_val = self.cloud_variables[name]
                else:
                    prev_val = None

                current_id = len(self.cloud_cache)

                cloud = CloudChange(name, value, current_id, previous_value = prev_val)
                self.cloud_variables.update({name: value})
                self.add_to_cloud_cache(RawCloudChange(name, value, current_id, previous_value = prev_val))

                for func_name, cloud_event_name in self.cloud_events.items():
                    if cloud_event_name == name:
                        cloud_event_task = self.cloud_event_task(cloud, func_name, name)
                        task = asyncio.create_task(cloud_event_task)
                        task.add_done_callback(self.raise_exc_callback)
                
                task = asyncio.create_task(self.on_message_event_task(cloud))
                task.add_done_callback(self.raise_exc_callback)

    async def cloud_event_task(self, cloud: CloudChange, func_name: str, error_func_name: str = None):
        """A cloud event task.
        Calls a function when an internally registered cloud variable changes.

        Internal.  
        """

        try:
            if not cloud.decoded and self.decoder:
                cloud.value = self.decoder(cloud.value)
                cloud.decoded = True
            await getattr(self, f'{func_name}')(cloud)
        except Exception as e:
            if error_func_name in self.cloud_event_errors:
                error_func = getattr(self, f'{self.cloud_event_errors[error_func_name]}')
                await error_func(cloud, e)
            else:
                raise e

    async def on_message_event_task(self, cloud: CloudChange):
        """The message task.
        Called whenever a cloud variable changes.
        If the on_message event is linked, calls on_message

        Internal.
        """

        try:
            if not cloud.decoded and self.decoder:
                cloud.value = self.decoder(cloud.value)
                cloud.decoded = True
            await self.on_message(cloud)
        except Exception as e:
            await self.on_message_error(cloud, e)
            return

    def raise_exc_callback(self, task: asyncio.Task):
        """A exception callback.

        Internal.
        """
        exception = task.exception()
        if exception:
            raise exception

    async def on_connect_task(self):
        """A coroutine that calls on_connect.

        Internal.
        """

        await self.on_connect()

    async def on_disconnect_task(self):
        """A coroutine that calls on_disconnect.

        Internal.
        """

        await self.on_disconnect()

    # EVENTS
    def event(self, func):
        """A decorator that registers on_message, on_connect, and, on_disconnect events.
        
        :param func: A function that will be registered. Must have an identical name to an event
        :type func: Callable

        The on_message event is called whenever the client recieves a CloudChange object

        The on_connect event is called whenever the client connects to the cloud

        The on_disconnect event is called whenever the client disconnects from the cloud

        Example Usage::

            @client.event
            async def on_message():
              print('We got a new message!')

            @client.event
            async def on_connect():
                print('Client connected to scratch!')
            
            @client.event
            async def on_disconnect():
                print('Client disconnected from scratch!')
        """

        f_name = func.__name__
        
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)

        if f_name == 'on_message':
            setattr(self, 'on_message', func)
            self.on_message_registered = True
            return wrap
        
        elif f_name == 'on_message_error':
            setattr(self, 'on_message_error', func)
            return wrap

        elif f_name == 'on_connect':
            setattr(self, 'on_connect', func)
            return wrap
        
        elif f_name == 'on_disconnect':
            setattr(self, 'on_disconnect', func)
            return wrap

    def cloud_event(self, variable_name: str):
        """A decorator that registers cloud events. Cloud events call specific functions whenever a specific variable changes. Using them takes away the user overhead of parsing each CloudChange object.
        
        :param variable_name: The variable name that will be registered
        :param variable_name: str

        :raises KeyError: If the cloud variable has already been registered

        Example Usage::
            
            @client.cloud_event('CloudVariableName')
            async def cloud_variable_name_changed(cloud: CloudChange):
              print(f'The variable CloudVariableName changed to {cloud.value}!')
        """

        def decorator(func):
            f_name = func.__name__
            c_name = f'_cloud_event_{f_name}'

            def wrap(*args, **kwargs):
                return func(*args, **kwargs)

            if c_name in self.cloud_events.keys():
                raise KeyError(f'cloud_event function with name {f_name} already exists.')
        
            self.cloud_events.update({c_name: variable_name})
            setattr(self, c_name, func)

            return wrap
        return decorator

    def cloud_event_error(self, variable_name: str):
        """A decorator that registers cloud error events. This coroutine is called whenever an error occurs in :meth:`cloud_event` for the same variable name. 
        
        :param variable_name: The variable name that will be registered
        :param variable_name: str

        :raises KeyError: If the cloud variable has already been registered

        Example Usage::

            @client.cloud_event('myvar')
            async def myvar_changed(cloud: CloudChange):
              print(f'2 divided by myvar is {2 / cloud.value}!')
            
            @client.cloud_event_error('myvar')
            async def myvar_error(cloud: CloudChange, error: Exception):
              if isinstance(error, ZeroDivisionError):
                print('Somebody entered a zero in myvar!)
        """

        def decorator(func):
            f_name = func.__name__
            c_name = f'_cloud_event_error_{f_name}'

            def wrap(*args, **kwargs):
                return func(*args, **kwargs)

            if c_name in self.cloud_events.values():
                raise KeyError(f'cloud_event_error for cloud variable {variable_name} already exists.')
        
            self.cloud_event_errors.update({variable_name: c_name})
            setattr(self, c_name, func)

            return wrap
        return decorator

    async def on_message(self, cloud: CloudChange):
        """The default value for on_message.

        :param cloud: An object that contains Cloud information
        :type cloud: :class:`client.CloudChange`

        Example Usage::

            @client.event
            async def on_message(cloud: CloudChange):
              print(f'{cloud.name} changed to {cloud.value}!')
        """

        pass

    async def on_message_error(self, cloud: CloudChange, error: Exception):
        """The default value for on_message_error. Called whenever an error occurs in :meth:`on_message`. 

        :param cloud: A cloudchange object that stores data from on_recv
        :type cloud: :class:`client.CloudChange`

        :param error: The exception raised in on_message
        :type error: :class:`Exception`
        
        Example Usage::

            @client.event
            async def on_message(cloud: CloudChange):
              if cloud.value.isdigit():
                val = int(cloud.value)
                print(100 / val)
            
            @client.event
            async def on_message_error(cloud: CloudChange, error: Exception):
              if isinstance(error, ZeroDivisionError):
                print('Somebody entered a zero!)
        """
        
        if self.on_message_registered:
            raise error

    async def on_connect(self):
        """The default value for on_connect.

        Example Usage::

            @client.event
            async def on_connect():
              print('Connected to Scratch :D')
        """

        pass

    async def on_disconnect(self):
        """The default value for on_disconnect.

        Example Usage::

            @client.event
            async def on_disconnect():
              print('Disconnected from Scratch D:')
        """

        pass

    ### CLOUD VARIABLES
    async def set_cloud(self, name: str, value: str, encode: bool = True):
        """A coroutine that sets cloud variables through the websocket connection. This must be called from another coroutine.

        :param name: The name of the cloud variable that will be set. This value must not include `"☁️ "`. A cloud variable named `"☁️ MyVariable"` should be refrenced here as `"MyVariable"`.
        :type name: str
        :param value: The value the cloud variable will be set to.
        :type value: str
        :param encode: Controls whether, if the client has an encoder, the encoder be used.
            Defaults to True
        :type encode: bool

        :raises TypeError: If the (possibly encoded) value is not digits
        :raises SizeError: If the value is larger than 256 digits

        Example Usage::

            @client.event
            async def on_connect():
              await client.set_cloud('MyCloudVariableName', '200')
            
        Note that above `client.set_cloud` is called from the `on_connect()` coroutine
        """

        value = str(value)

        if self.encoder and encode:
            value = self.encoder(value)
        
        if not (value.isdigit() or value == ''):
            raise TypeError('Cloud value must be digits')

        if len(value) > 256:
            raise SizeError('Cloud value length must be under or equal to 256 digits.')
        
        payload = {
            'method': 'set',
            'name': f'☁ {name}',
            'value': value,
            'user': self.username,
            'project_id': self.project_id,
        }

        await self.ws_send(payload)
        if name in self.cloud_variables:
            prev = self.cloud_variables[name]
        else:
            prev = None

        current_id = len(self.cloud_cache)
        self.add_to_cloud_cache(RawCloudChange(name, value, current_id, previous_value=prev, sender=self))
        self.cloud_variables.update({name: value})

    def parse_raw_cloud(self, raw_data: str) -> dict:
        """A method that parses data received directly from the websocket
        
        :param raw_data: The data to be parsed
        :type raw_data: str

        :rtype: dict
        
        Internal.
        """

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
    
    def add_to_cloud_cache(self, item):
        """Adds an item to the cloud cache. If the cloud cache is too long, delete the least recent item to be added.
        
        Internal.

        :param item: the item that will be added
        """

        self.cloud_cache.append(item)
        if len(self.cloud_cache) > self.max_cache_length:
            self.cloud_cache.pop(0)