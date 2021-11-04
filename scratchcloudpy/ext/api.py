from requests.models import Response
from ..client import CloudClient
import asyncio
import aiohttp
import time
import requests
import json

class NotFound(dict): pass

def get_keys(d: dict, keys: list, if_not_found = NotFound()):
    for key in keys:
        try: 
            d = d[key]
        except:
            return if_not_found
    return d

class APIClient (CloudClient):
    pass

# api.scratch.mit.edu/users/User
class User():
    def __init__(self, session: aiohttp.ClientSession, **kwargs):
        self.session = session
        self._update_all(kwargs)

    def _update_all(self, data):
        self.id = get_keys(data, ['id'])
        self.name = get_keys(data, ['username'])
        self.scratchteam = get_keys(data, ['scratchteam'])
        self.joined = get_keys(data, ['history', 'joined'])
        
        self.image_90x90 = get_keys(data, ['profile', 'images', '90x90'])
        self.image_60x60 = get_keys(data, ['profile', 'images', '60x60'])
        self.image_55x55 = get_keys(data, ['profile', 'images', '55x55'])
        self.image_50x50 = get_keys(data, ['profile', 'images', '50x50'])
        self.image_32x32 = get_keys(data, ['profile', 'images', '32x32'])

        self.status = get_keys(data, ['profile', 'status'])
        self.bio = get_keys(data, ['profile', 'bio'])
        self.country = get_keys(data, ['profile', 'bio'])

    async def fetch_api(self):
        data = await self.session.get(f'https://api.scratch.mit.edu/users/{self.name}')
        data = await data.json()
        self.__init__(self.session, **data)

    def __setattr__(self, name: str, value) -> None:
        if not (isinstance(value, NotFound) and name in self.__dict__.keys()):
            self.__dict__[name] = value

class Author(User):
    pass

class Project():
    def __init__(self, session: aiohttp.ClientSession, **kwargs):
        self.session = session
        
        self._update_all(kwargs)


    def _update_all(self, data):
        self.id = get_keys(data, ['id'])
        self.title = get_keys(data, ['title'])
        self.description = get_keys(data, ['description'])
        self.instructions = get_keys(data, ['instructions'])
        self.visibility = get_keys(data, ['visibility'])
        self.public = get_keys(data, ['public'])
        self.comments_allowed = get_keys(data, ['comments_allowed'])
        self.is_published = get_keys(data, ['is_published'])

        self.author = Author(self.session, **get_keys(data, ['author']))

        self.image = get_keys(data, ['image'])
        self.created = get_keys(data, ['history', 'created'])
        self.modified = get_keys(data, ['history', 'modified'])
        self.shared = get_keys(data, ['history', 'shared'])

        self.views = get_keys(data, ['stats', 'views'])
        self.loves = get_keys(data, ['stats', 'loves'])
        self.favorites = get_keys(data, ['stats', 'favorites'])
        self.remixes = get_keys(data, ['stats', 'remixes'])

        self.remix_parent = get_keys(data, ['remix', 'parent'])
        self.remix_root = get_keys(data, ['remix', 'root'])



    async def fetch_api(self):
        data = await self.session.get(f'https://api.scratch.mit.edu/projects/{self.id}')
        data = await data.json()
        self.__init__(self.session, **data)
    
    def __setattr__(self, name: str, value) -> None:
        if not (isinstance(value, NotFound) and name in self.__dict__.keys()):
            self.__dict__[name] = value    

    
