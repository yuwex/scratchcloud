from textwrap import wrap
import asyncio

from ..client import CloudClient, SizeError, CloudChange
from ..errors import MissingCloudVariable, UnableToValidate

class SegmentDump:
    """A utility for sending and reading large data.
    This class reads large data by breaks it into segments.
    
    :param client: The client that will be used for operations
    :type client: :class:`client.CloudClient`
    :param cloud_names: The cloud variables that will be set and read
    :type cloud_names: list[str]

    :raises MissingCloudVariable: If not all cloud_names are found in the cached cloud variables
    """

    def __init__(self, client: CloudClient, cloud_names: list[str]):
        self.client = client
        self.cloud_names = cloud_names
        
        self.MAX_CLOUD_LENGTH: int = 256

    def dict_has_all_keys(self, d: dict, keys: list[str]):
        return not any([key not in d for key in keys])

    def get_segments(self, data: str, encode_data: bool = False, empty_value: str = '0', encode_empty: bool = False) -> dict:
        """A function that breaks up data into 256-length segment. Returns a dict with the cloud variable name and the segment.

        :param data: The data that will be sent
        :type data: str
        :param encode_data: A boolean that encodes the data if true,
            default false
        :type encode_data: bool
        :param empty_value: The value that unused segments are set to,
            default '0'
        :type empty_value: str
        :param encode_empty: A boolean that encodes the empty value,
            default False
        :type encode_empty: bool

        :raises ValueError: If the value that will be encoded is not digits
        :raises SizeError: If the data that will be sent is larger than the maximum length

        :rtype: dict
        """

        if self.client.encoder and encode_data:
            data = self.client.encoder(data)

        if self.client.encoder and encode_empty:
            empty_value = self.client.encoder(empty_value)

        if not empty_value.isdigit():
            raise ValueError('empty_value must digits. Maybe you meant to use encode_empty=True?')

        if len(data) > (self.MAX_CLOUD_LENGTH * len(self.cloud_names)):
            raise SizeError(f'Your data is too big! Must be less than or equal to {(self.MAX_CLOUD_LENGTH * len(self.cloud_names))} characters.')

        segments = {}

        pieces = wrap(data, self.MAX_CLOUD_LENGTH)
        for index, name in enumerate(self.cloud_names):
            if len(pieces) > index:
                segments.update({name: pieces[index]})
            else:
                segments.update({name: empty_value})
        
        return segments

    async def dump(self, data: str, delay: float = 0.01, encode_data: bool = False, empty_value: str = '0', encode_empty: bool = False):
        """A asynchronous method to dump data to several variables at once. Pretty much a wrapper for get_segments that sends data as well.
        
        :param data: The data that will be sent
        :type data: str
        :param encode_data: A boolean that encodes the data if true,
            default false
        :type encode_data: bool
        :param delay: The delay between setting different cloud variables,
            default 0.01
        :type delay: float
        :param empty_value: The value that unused segments are set to,
            default '0'
        :type empty_value: str
        :param encode_empty: A boolean that encodes the empty value,
            default False
        :type encode_empty: bool

        :raises ValueError: If the value that will be encoded is not digits
        :raises SizeError: If the data that will be sent is larger than the maximum length
        :raises MissingCloudVariable: If the specified cloud variables don't exist in the project
        """

        if not self.dict_has_all_keys(self.client.cloud_variables, self.cloud_names):
            raise MissingCloudVariable('cloud_names not found in project')

        segments = self.get_segments(data, encode_data, empty_value, encode_empty)
        
        for cloud_name, cloud_value in segments.items():
            await self.client.set_cloud(cloud_name, cloud_value, encode = False)
            await asyncio.sleep(delay)
        
        return segments

    def read(self, decode_data: bool = False, end_var_value: str = '0', encode_end: bool = False) -> str:
        """A method to read data from several variables at once.
        
        :param decode_data: A boolean that decodes the data if true,
            default False
        :type decode_data: bool
        :param end_var_value: The value of empty data
            default '0'
        :type end_var_value: str
        :param encode_end: A boolean that encodes end_var_value before searching for it,
            default false
        :type encode_end: bool

        :rtype: str

        :raises MissingCloudVariable: If the specified cloud variables don't exist in the project
        """

        if not self.dict_has_all_keys(self.client.cloud_variables, self.cloud_names):
            raise MissingCloudVariable('cloud_names not found in project')

        payload = ''
        if self.client.encoder and encode_end:
            end_var_value = self.client.encoder(end_var_value)
        
        for name in self.cloud_names:
            value = self.client.cloud_variables[name]
            if value == end_var_value: break

            payload += value

        if decode_data and self.client.decoder:
            payload = self.client.decoder(payload)
        
        return payload
        
class CloudValidator:
    """A utility for getting the sender of CloudChange objects.
    This class validates a CloudChange variable adding the sender attribute.
    
    :param client: The client that will be used for operations
    :type client: :class:`client.CloudClient`
    """

    def __init__(self, client: CloudClient):
        self.client = client
        
    async def validate_cloud(self, cloud: CloudChange):
        """A method to validate and return the sender of a CloudChange object.
        
        :param cloud: A CloudChange object that will be validated
        :type cloud: `client.CloudChange`

        :raises UnableToValidate: If the CloudChange object could not be validated

        :rtype: str
        """

        PATH = f'https://clouddata.scratch.mit.edu/logs?projectid={self.client.project_id}&limit=50&offset=0'
        
        current_cache = self.client.cloud_cache.copy()
        
        data = await self.client.http_session.get(PATH)
        data = await data.json()

        clouddata = []
        for event in data:
            if event['verb'] == 'set_var':
                clouddata.append(event)
        
        index = None
        for count, cached_cloud in enumerate(current_cache):
            if cached_cloud.id == cloud.id:
                raw_cloud = cached_cloud
                index = len(current_cache) - count - 1
                break
        
        if index is None:
            raise UnableToValidate('CloudChange could not be found in cache')

        api_data = clouddata[index]
        if not api_data['value'] == raw_cloud.value:
            raise UnableToValidate('CloudChange value was different from cloud api value')

        sender = clouddata[index]['user']

        cloud.sender = sender
        return sender