from requests.models import Response
from ..client import CloudClient
import asyncio
import aiohttp
import time
import requests
import json

class APIClient (CloudClient):
    pass


# api.scratch.mit.edu/users/User
class User():
    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        
        self.id = kwargs['id']
        self.name = kwargs['username']
        self.scratchteam = kwargs['scratchteam']
        self.joined = kwargs['history']['joined']
        
        self.image_90x90 = kwargs['profile']['images']['90x90']
        self.image_60x60 = kwargs['profile']['images']['60x60']
        self.image_55x55 = kwargs['profile']['images']['55x55']
        self.image_50x50 = kwargs['profile']['images']['50x50']
        self.image_32x32 = kwargs['profile']['images']['32x32']

        self.status = kwargs['profile']['status']
        self.bio = kwargs['profile']['bio']
        self.country = kwargs['profile']['country']

class Author(User):
    pass
