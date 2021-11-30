from typing import List
from textwrap import wrap
import asyncio

from ..client import CloudClient, SizeError

class MissingCloudVariable(Exception): pass

class SegmentDump:
    def __init__(self, client: CloudClient, cloud_names: list):
        self.client = client
        self.cloud_names = cloud_names
        
        self.MAX_CLOUD_LENGTH: int = 256

    def dict_has_all_keys(self, d: dict, keys: List['str']):
        return not any([key not in d for key in keys])

    async def dump(self, data: str, encode_data: bool = False, delay: float = 0.01, empty_value: str = '0', encode_empty: bool = False):
        if not self.dict_has_all_keys(self.client.cloud_variables, self.cloud_names):
            raise MissingCloudVariable('cloud_names not found in project')
        
        if self.client.encoder and encode_data:
            data = self.client.encoder(data)

        if self.client.encoder and encode_empty:
            empty_value = self.client.encoder(empty_value)

        if not empty_value.isdigit():
            raise TypeError('empty_value must digits')

        if len(data) > (self.MAX_CLOUD_LENGTH * len(self.cloud_names)):
            raise SizeError(f'Your data is too big! Must be less than or equal to {(self.MAX_CLOUD_LENGTH * len(self.cloud_names))} characters.')

        segments = {}

        pieces = wrap(data, 256)
        for index, name in enumerate(self.cloud_names):
            if len(pieces) >= index:
                segments.update({name: pieces[index]})
            else:
                segments.update({name: empty_value})
        
        for cloud_name, cloud_value in segments.items():
            await self.client.set_cloud(cloud_name, cloud_value, encode = False)
            await asyncio.sleep(delay)
        
        return segments
            
    def read(self, decode_data: bool = False, end_var_value: str = '0', encode_end: bool = False) -> str:
        if not self.dict_has_all_keys(self.client.cloud_variables, self.cloud_names):
            raise MissingCloudVariable('cloud_names not found in project')
        
        payload = ''
        if self.client.encoder and encode_end:
            end_var_value = self.client.encoder(end_var_value)
        
        print(self.client.cloud_variables)
        for name in self.cloud_names:
            value = self.client.cloud_variables[name]
            if value == end_var_value: break

            payload += value

        if decode_data and self.client.decoder:
            payload = self.client.decoder(payload)
        
        return payload
        
        