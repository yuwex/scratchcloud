from __future__ import annotations
from typing import List, Union
from datetime import datetime
from enum import Enum
from dataclasses import InitVar, dataclass
import json

from ..client import CloudClient
from ..errors import NotFoundError

class APIConnection:
    """An interface that connects to the base scratch API.
    """

    def __init__(self, client: CloudClient):
        self.client: CloudClient = client
    
    async def fetch_user(self, user: Union[str, 'User', 'IncompleteUser']) -> 'User':
        """A coroutine that fetches a user from the API.
        
        :param user: A username or object that inherits from `ext.api.User`
        :raises NotFoundError: If the data couldn't be accessed by the scratch API

        :rtype: :class:`ext.api.User`
        """

        # Type checking: user
        if isinstance(user, str):
            username = user
        elif isinstance(user, User):
            username = user.username
        else:
            raise TypeError('user must be of type str, User, or IncompleteUser')

        PATH = f'https://api.scratch.mit.edu/users/{username}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()
        if 'code' in data:
            raise NotFoundError()
        
        return User(self, **data)
    
    async def fetch_project(self, project: Union[int, str, 'Project', 'IncompleteProject']) -> 'Project':
        """A coroutine that fetches a project from the API.
        
        :param owner_username: The username of the owner of the project
        :type owner_username: str
        :param project: The id of the project or a object that inherits from `ext.api.Project`

        :raises NotFoundError: If the data couldn't be accessed by the scratch API

        :rtype: :class:`ext.api.Project`
        """

        # Type checking: project
        if isinstance(project, int):
            project_id = project
        elif isinstance(project, str):
            if project.isdigit():
                project_id = int(project)
            else:
                raise TypeError(f'Project type of str must be digits, not {project}')
        elif isinstance(project, Project):
            project_id = project.id

        PATH = f'https://api.scratch.mit.edu/projects/{project_id}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()
        if 'code' in data:
            raise NotFoundError()
        
        return Project(self, **data)
        
    async def fetch_studio(self, studio: Union[str, int, 'Studio']) -> 'Studio':
        """A coroutine that fetches a studio from the API.
        
        :param studio: The studio id or `ext.api.Studio` object.

        :raises NotFoundError: If the data couldn't be accessed by the scratch API

        :rtype: :class:`ext.api.Studio`
        """

        # Type checking: project
        if isinstance(studio, int):
            studio_id = studio
        elif isinstance(studio, str):
            if studio.isdigit():
                studio_id = int(studio)
            else:
                raise TypeError(f'Studio type of str must be digits, not {studio}')
        elif isinstance(studio, Studio):
            studio_id = studio.id

        PATH = f'https://api.scratch.mit.edu/studios/{studio_id}'
        data = await self.client.http_session.get(PATH)
        data = await data.json()
        if 'code' in data:
            raise NotFoundError()
        
        return Studio(self, **data)

@dataclass
class User:
    connection: APIConnection
    id: int
    username: str
    
    scratchteam: int = None

    history: InitVar[dict] = None
    joined: datetime = None
        
    profile: InitVar[dict] = None
    status: str = None
    bio: str = None
    country: str = None
    image: str = None

    def __post_init__(self, history, profile):
        if history:
            self.joined = datetime.strptime(history['joined'], "%Y-%m-%dT%H:%M:%S.%f%z")
        
        if profile:
            self.image = profile['images']['90x90']

            if 'country' in profile:
                self.status = profile['status']
                self.bio = profile['bio']
                self.country = profile['country']
    
    async def fetch_favorite_projects(self, limit: int = 20, offset: int = 0) -> List[Project]:
        """Fetches the user's favorite projects.
        
        :param limit: The maximum number of return values,
            default 20
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.Project`]
        """

        PATH = f'https://api.scratch.mit.edu/users/{self.username}/favorites?limit={limit}&offset={offset}'
        data = await self.connection.client.http_session.get(PATH)
        data = await data.json()

        return [Project(connection=self.connection, **project) for project in data]

    async def fetch_projects(self, limit: int = 20, offset: int = 0) -> List[Project]:
        """Fetches the user's projects.
        
        :param limit: The maximum number of return values,
            default 20
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.Project`]
        """

        PATH = f'https://api.scratch.mit.edu/users/{self.username}/projects?limit={limit}&offset={offset}'
        data = await self.connection.client.http_session.get(PATH)
        data = await data.json()

        return [Project(connection=self.connection, **project) for project in data]

    async def fetch_followers(self, limit: int = 20, offset: int = 0) -> List[User]:
        """Fetches the user's followers.
        
        :param limit: The maximum number of return values,
            default 20
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.User`]
        """

        PATH = f'https://api.scratch.mit.edu/users/{self.username}/followers?limit={limit}&offset={offset}'
        data = await self.connection.client.http_session.get(PATH)
        data = await data.json()

        return [User(connection=self.connection, **user) for user in data]

    async def fetch_following(self, limit: int = 20, offset: int = 0) -> List[User]:
        """Fetches who the user is following.
        
        :param limit: The maximum number of return values,
            default 20
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.User`]
        """

        PATH = f'https://api.scratch.mit.edu/users/{self.username}/following?limit={limit}&offset={offset}'
        data = await self.connection.client.http_session.get(PATH)
        data = await data.json()

        return [User(connection=self.connection, **user) for user in data]

    async def fetch_message_count(self) -> int:
        """Fetches the user's number of unread messages.
        
        :rtype: int
        """

        PATH = f'https://api.scratch.mit.edu/users/{self.username}/messages/count'
        data = await self.connection.client.http_session.get(PATH)
        data = await data.json()
        return data['count']

@dataclass
class IncompleteUser(User):
    image: str = None

@dataclass
class Project:
    connection: APIConnection
    id: int
    title: str

    description: str = None
    instructions: str = None
    visibility: str = None
    public: bool = None
    comments_allowed: bool = None
    is_published: bool = None
    image: str = None

    author: IncompleteUser | InitVar[dict] = None

    history: InitVar[dict] = None
    created: datetime = None
    modified: datetime = None
    shared: datetime = None

    stats: InitVar[dict] = None
    views: int = None
    loves: int = None
    favorites: int = None
    remixes: int = None

    remix: InitVar[dict] = None
    parent_id: int = None
    root_id: int = None

    images: InitVar[dict] = None

    def __post_init__(self, author, history, stats, remix, images):
        if author:
            self.author = IncompleteUser(self.connection, **author)
        
        if history:
            self.created = datetime.strptime(history['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
            self.modified = datetime.strptime(history['modified'], "%Y-%m-%dT%H:%M:%S.%f%z")
            self.shared = datetime.strptime(history['shared'], "%Y-%m-%dT%H:%M:%S.%f%z")

        if stats:
            self.views = stats['views']
            self.loves = stats['loves']
            self.favorites = stats['favorites']
            self.remixes = stats['remixes']
        
        if remix:
            self.parent_id = remix['parent']
            self.root_id = remix['root']
    
    async def fetch_comments(self, limit: int = 20, offset: int = 0) -> List[Comment]:
        """Fetches the project's comments.
        
        :param limit: The maximum number of return values,
            default 20
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.Comment`]
        """

        comment_path = f'https://api.scratch.mit.edu/users/{self.author.username}/projects/{self.id}/comments'
        extension = f'?offset={offset}&limit={limit}'
        data = await self.connection.client.http_session.get(f'{comment_path}{extension}')
        data = await data.json()

        return [Comment(connection=self.connection, type=CommentType.Project, api_path=comment_path, **comment) for comment in data]

    async def fetch_project_json_object(self) -> ProjectJSON:
        """Fetches the project's json from the api.

        :rtype: ProjectJSON
        """

        PATH = f'https://projects.scratch.mit.edu/{self.id}/'
        data = await self.connection.client.http_session.get(PATH)
        data = await data.json()

        return ProjectJSON(data)

@dataclass
class IncompleteProject(Project):
    pass

@dataclass
class StudioProject(IncompleteProject):
    actor_id: int = None

@dataclass
class ProjectJSON(dict):

    def __init__(self, *args, **kwargs):
        super(ProjectJSON, self).__init__(*args, **kwargs)

    def get_block_count(self) -> int:
        return sum([len(sprite['blocks']) for sprite in self['targets']])

    def get_sprite_count(self) -> int:
        return len(self['targets']) - 1 # Remove stage from sprites

    def get_json(self, *args, **kwargs) -> str:
        return json.dumps(self, *args, **kwargs)

@dataclass
class Studio:
    connection: APIConnection
    id: int
    title: str

    host: int = None
    description: str = None
    visibility: str = None
    public: bool = None
    open_to_all: bool = None
    comments_allowed: bool = None
    image: str = None

    history: InitVar[dict] = None
    created: datetime = None
    modified: datetime = None

    stats: InitVar[dict] = None
    comments: int = None
    followers: int = None
    managers: int = None
    projects: int = None

    def __post_init__(self, history, stats):
        if history:
            self.created = datetime.strptime(history['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
            self.modified = datetime.strptime(history['modified'], "%Y-%m-%dT%H:%M:%S.%f%z")

        if stats:
            self.comments = stats['comments']
            self.followers = stats['followers']
            self.managers = stats['managers']
            self.projects = stats['projects']
    
    async def fetch_projects(self, limit: int = 24, offset: int = 0) -> List[StudioProject]:
        """Fetches the studio's projects.
        
        :param limit: The maximum number of return values, optional
            default 24
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.Project`]
        """

        PATH = f'https://api.scratch.mit.edu/studios/{self.id}/projects/?limit={limit}&offset={offset}'
        data = await self.connection.client.http_session.get(PATH)
        data = await data.json()

        projects = []
        for project in data:
            projects.append(StudioProject(
                connection = self.connection,
                id = project['id'],
                title = project['title'],
                image = project['image'],
                actor_id = project['actor_id'],
                author = {
                    'id': project['creator_id'],
                    'username': project['username'],
                    'image': project['avatar']['90x90']
                }
            ))
        
        return project

    async def fetch_comments(self, limit: int = 20, offset: int = 0) -> List[Comment]:
        """Fetches the studio's comments.
        
        :param limit: The maximum number of return values,
            default 20
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.Comment`]
        """

        comment_path = f'https://api.scratch.mit.edu/studios/{self.id}/comments'
        extension = f'?limit={limit}&offset={offset}'
        data = await self.connection.client.http_session.get(f'{comment_path}{extension}')
        data = await data.json()

        return [Comment(connection=self.connection, type=CommentType.Studio, api_path=comment_path, **comment) for comment in data]

    async def fetch_managers(self, limit: int = 40, offset: int = 0) -> List[User]:
        """Fetches the studio's managers from the api.
        
        :param limit: The maximum number of return values,
            default 40
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.StudioUser`]
        """

        PATH = f'https://api.scratch.mit.edu/studios/{self.id}/managers/?limit={limit}&offset={offset}'
        data = await self.connection.client.http_session.get(PATH)
        data = await data.json()

        return [User(connection=self.connection, **user) for user in data]

    async def fetch_curators(self, limit: int = 40, offset: int = 0) -> List[User]:
        """Fetches the studio's curators.
        
        :param limit: The maximum number of return values,
            default 40
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.StudioUser`]
        """

        PATH = f'https://api.scratch.mit.edu/studios/{self.id}/curators/?limit={limit}&offset={offset}'
        data = await self.connection.client.http_session.get(PATH)
        data = await data.json()

        return [User(connection=self.connection, **user) for user in data]

class CommentType(Enum):
    Project = 0
    Studio = 1

@dataclass
class Comment:
    connection: APIConnection
    type: CommentType
    api_path: str

    id: int
    
    parent_id: int = None
    commentee_id: int = None
    content: str = None

    datetime_created: InitVar[str] = None
    created: datetime = None

    datetime_modified: InitVar[str] = None
    modified: datetime = None

    visibility: str = None

    author: InitVar[dict] = None

    reply_count: int = None

    def __post_init__(self, datetime_created, datetime_modified, author):
        if datetime_created:
            self.created = datetime.strptime(datetime_created, "%Y-%m-%dT%H:%M:%S.%f%z")

        if datetime_modified:
            self.modified = datetime.strptime(datetime_modified, "%Y-%m-%dT%H:%M:%S.%f%z")
        
        if author:
            self.author = IncompleteUser(self.connection, **author)
    
    async def fetch_replies(self, limit: int = 20, offset: int = 0) -> List[Comment]:
        """Fetches the comment's replies.
        
        :param limit: The maximum number of return values,
            default 20
        :type limit: int, optional
        :param offset: The offset for return values,
            default 0
        :type offset: int, optional

        :rtype: List[:class:`ext.api.Reply`]
        """

        data = await self.connection.client.http_session.get(f'{self.api_path}/{self.id}/replies?limit={limit}&offset={offset}')
        data = await data.json()

        return [Comment(connection=self.connection, type=self.type, api_path=self.api_path, **comment) for comment in data]