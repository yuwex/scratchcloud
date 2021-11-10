from __future__ import annotations

from ..client import CloudClient
from datetime import datetime
import asyncio
import aiohttp
import time
import json
from enum import Enum

from typing import List

class NotFound(): pass

class NotFoundError(Exception): pass

def get_keys(d: dict, keys: list, if_not_found = NotFound()):
    for key in keys:
        try: 
            d = d[key]
        except:
            return if_not_found
    return d

class APIClient (CloudClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def fetch_user(self, username: str) -> 'User':
        PATH = f'https://api.scratch.mit.edu/users/{username}'
        data = await self.http_session.get(PATH)
        data = await data.json()
        if 'code' in data:
            if data['code'] == 'NotFound':
                raise NotFoundError()
        
        return User(self, **data)
    
    async def fetch_project(self, owner_username: str, project_id: str) -> 'Project':
        PATH = f'https://api.scratch.mit.edu/users/{owner_username}/projects/{project_id}'
        data = await self.http_session.get(PATH)
        data = await data.json()
        if 'code' in data:
            if data['code'] == 'NotFound':
                raise NotFoundError()
        
        return Project(self, **data)
        
    async def fetch_studio(self, studio_id: str) -> 'Studio':
        PATH = f'https://api.scratch.mit.edu/{studio_id}'
        data = await self.http_session.get(PATH)
        data = await data.json()
        if 'code' in data:
            if data['code'] == 'NotFound':
                raise NotFoundError()
        
        return Studio(self, **data)

class BaseScratchObject():
    def __setattr__(self, name: str, value) -> None:
        if not (isinstance(value, NotFound) and name in self.__dict__.keys()):
            self.__dict__[name] = value  

class User(BaseScratchObject):
    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        self._update_all(kwargs)

    def _update_all(self, data):
        self.id = get_keys(data, ['id'])
        self.name = get_keys(data, ['username'])
        self.scratchteam = get_keys(data, ['scratchteam'])
        self.joined_at = get_keys(data, ['history', 'joined'])
        if type(self.joined_at) == 'str':
            self.joined_at = datetime.strptime(self.joined_at, "%Y-%m-%dT%H:%M:%S.%f%z")
        
        self.image_90x90 = get_keys(data, ['profile', 'images', '90x90'])
        self.image_60x60 = get_keys(data, ['profile', 'images', '60x60'])
        self.image_55x55 = get_keys(data, ['profile', 'images', '55x55'])
        self.image_50x50 = get_keys(data, ['profile', 'images', '50x50'])
        self.image_32x32 = get_keys(data, ['profile', 'images', '32x32'])

        self.status = get_keys(data, ['profile', 'status'])
        self.bio = get_keys(data, ['profile', 'bio'])
        self.country = get_keys(data, ['profile', 'country'])

    async def fetch_api(self):
        PATH = f'https://api.scratch.mit.edu/users/{self.name}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()
        self._update_all(data)
    
    async def fetch_message_count(self) -> int:
        PATH = f'https://api.scratch.mit.edu/users/{self.name}/messages/count'
        data = await self.client.http_session.get(PATH)
        data = await data.json()
        return data['count']
    
    async def fetch_favorites(self, limit: int = 20, offset: int = 0) -> List[Project]:
        PATH = f'https://api.scratch.mit.edu/users/{self.name}/favorites?limit={limit}&offset={offset}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()

        projects = []
        for project in data:
            projects.append(Project(client=self.client, **project))
        
        return projects

    async def fetch_followers(self, limit: int = 20, offset: int = 0) -> List[User]:
        PATH = f'https://api.scratch.mit.edu/users/{self.name}/followers?limit={limit}&offset={offset}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()

        users = []
        for user in data:
            users.append(User(client=self.client, **user))
        
        return users

    async def fetch_following(self, limit: int = 20, offset: int = 0) -> List[User]:
        PATH = f'https://api.scratch.mit.edu/users/{self.name}/following?limit={limit}&offset={offset}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()

        users = []
        for user in data:
            users.append(User(client=self.client, **user))
        
        return users

    async def fetch_projects(self, limit: int = 20, offset: int = 0) -> List[Project]:
        PATH = f'https://api.scratch.mit.edu/users/{self.name}/projects?limit={limit}&offset={offset}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()

        projects = []
        for project in data:
            projects.append(Project(client=self.client, **project))
        
        return projects

class Author(User):
    pass

class CommentType(Enum):
    Project = 0
    Studio = 1
    Profile = 2

class Comment(BaseScratchObject):
    def __init__(self, client: APIClient, comment_type: CommentType, **kwargs):
        self.client = client
        self.comment_type = comment_type

        self._update_all(kwargs)
    
    def _update_all(self, data):
        if self.comment_type.value == 0: # Project type
            self.project: Project = get_keys(data, ['project'])
        if self.comment_type.value == 1: # Studio type
            self.studio: Studio = get_keys(data, ['studio'])

        self.id = get_keys(data, ['id'])
        self.parent_id = get_keys(data, ['parent_id'])
        self.parent_author_id = get_keys(data, ['commentee_id'])
        self.content = get_keys(data, ['content'])

        self.created_at = get_keys(data, ['datetime_created'])
        if type(self.created_at) == 'str':
            self.created_at = datetime.strptime(self.created_at, "%Y-%m-%dT%H:%M:%S.%f%z")

        self.modified_at = get_keys(data, ['datetime_modified'])
        if type(self.modified_at) == 'str':
            self.modified_at = datetime.strptime(self.modified_at, "%Y-%m-%dT%H:%M:%S.%f%z")

        self.visibility = get_keys(data, ['visibility'])
        self.reply_count = get_keys(data, ['reply_count']) 

        self.author = Author(self.client, **get_keys(data, ['author']))
    
    async def fetch_replies(self, offset: int = 0, limit: int = 20) -> List[Reply]:
        if self.comment_type.value == 0: # Project type
            PATH = f'https://api.scratch.mit.edu/users/{self.project.author.name}/projects/{self.project.id}/comments/{self.id}/replies?offset={offset}&limit={limit}'
        elif self.comment_type.value == 1: # Studio type
            PATH = f'https://api.scratch.mit.edu/studios/{self.studio.id}/comments/{self.id}/replies?offset={offset}&limit={limit}'
        
        data = await self.client.http_session.get(PATH)
        data = await data.json()

        comments = []
        for comment in data:
            if self.comment_type.value == 0: # Project type
                comments.append(Reply(self.client, self.comment_type, project = self.project, **comment))
            elif self.comment_type.value == 1: # Studio type
                comments.append(Reply(self.client, self.comment_type, studio = self.studio, **comment))

        return comments

class Reply(Comment):
    pass

class Project(BaseScratchObject):
    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        self.project_json = None
        
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

        self.author = Author(self.client, **get_keys(data, ['author']))

        self.image = get_keys(data, ['image'])
        self.created_at = get_keys(data, ['history', 'created'])
        if type(self.created_at) == 'str':
            self.created_at = datetime.strptime(self.created_at, "%Y-%m-%dT%H:%M:%S.%f%z")

        self.modified_at = get_keys(data, ['history', 'modified'])
        if type(self.modified_at) == 'str':
            self.modified_at = datetime.strptime(self.modified_at, "%Y-%m-%dT%H:%M:%S.%f%z")

        self.shared_at = get_keys(data, ['history', 'shared'])
        if type(self.shared_at) == 'str':
            self.shared_at = datetime.strptime(self.shared_at, "%Y-%m-%dT%H:%M:%S.%f%z")
         


        self.views = get_keys(data, ['stats', 'views'])
        self.loves = get_keys(data, ['stats', 'loves'])
        self.favorites = get_keys(data, ['stats', 'favorites'])
        self.remixes = get_keys(data, ['stats', 'remixes'])

        self.remix_parent = get_keys(data, ['remix', 'parent'])
        self.remix_root = get_keys(data, ['remix', 'root'])

    async def fetch_api(self):
        PATH = f'https://api.scratch.mit.edu/projects/{self.id}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()
        self._update_all(data)
    
    async def fetch_comments(self, offset: int = 0, limit: int = 20) -> List[Comment]:
        PATH = f'https://api.scratch.mit.edu/users/{self.author.name}/projects/{self.id}/comments?offset={offset}&limit={limit}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()
        
        comments = []
        for comment in data:
            comments.append(Comment(self.client, CommentType(0), project = self, **comment))
        
        return comments
    
    async def fetch_project_json(self):
        PATH = f'https://projects.scratch.mit.edu/{self.id}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()

        self.project_json = data
        return data

    async def fetch_block_count(self):
        project = await self.fetch_project_json()

        blocks = 0
        for sprite in project['targets']:
            blocks += len(sprite['blocks'])
    
        return blocks
    
    async def fetch_sprite_count(self):
        project = await self.fetch_project_json()

        sprites = 0
        for sprite in project['targets']:
            sprites += 1
    
        return sprites

class StudioProject(Project):
    pass

class Studio(BaseScratchObject):
    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        self._update_all(kwargs)
    
    def _update_all(self, data):
        self.id = get_keys(data, ['id'])
        self.title = get_keys(data, ['title'])
        self.host_id = get_keys(data, ['host'])
        self.description = get_keys(data, ['description'])
        self.visibility = get_keys(data, ['visibility'])
        self.public = get_keys(data, ['public'])
        self.open_to_all = get_keys(data, ['open_to_all'])
        self.comments_allowed = get_keys(data, ['comments_allowed'])
        self.image = get_keys(data, ['image'])

        self.created_at = get_keys(data, ['created'])
        if type(self.created_at) == 'str':
            self.created_at = datetime.strptime(self.created_at, "%Y-%m-%dT%H:%M:%S.%f%z")

        self.modified_at = get_keys(data, ['modified'])
        if type(self.modified_at) == 'str':
            self.modified_at = datetime.strptime(self.modified_at, "%Y-%m-%dT%H:%M:%S.%f%z")

        self.num_comments = get_keys(data, ['comments'])
        self.num_followers = get_keys(data, ['followers'])
        self.num_managers = get_keys(data, ['managers'])
        self.num_projects = get_keys(data, ['projects'])

    async def fetch_api(self):
        PATH = f'https://api.scratch.mit.edu/studios/{self.id}'
        data = await self.client.http_session.get(PATH)
        data = await data.json
        self._update_all(data)

    async def fetch_projects(self, offset: int = 0, limit: int = 24):
        PATH = f'https://api.scratch.mit.edu/studios/{self.id}/projects/'
        data = await self.client.http_session.get(PATH)
        data = await data.json()
        projects = []
        for proj in data:
            projects.append(
                StudioProject(
                    client = self.client,

                    id = proj['id'], 
                    title = proj['title'], 
                    image = proj['image'], 
                    author = {
                        'id': proj['creator_id'],
                        'username': proj['username']
                    }
            ))
        
        return projects

    async def fetch_comments(self, offset: int = 0, limit: int = 20):
        PATH = f'https://api.scratch.mit.edu/studios/{self.id}/comments?offset={offset}&limit={limit}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()

        comments = []
        for comment in data:
            comments.append(Comment(self.client, CommentType(1), studio = self, **comment))
        
        return comments

# TODO
# Change ClientSession uses to APIClient
# Add Regex for site-api (followers#, following#, etc)
# Add /site-api/ methods
# Add ValidateCloud
