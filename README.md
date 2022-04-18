# scratchcloud
An asynchronous Pythonic wrapper for scratch.mit.edu cloud websockets.

[![PyPi Package Version](https://img.shields.io/pypi/v/scratchcloud)](https://pypi.org/project/scratchcloud/)
[![PyPi Package Python Versions](https://shields.io/pypi/pyversions/scratchcloud)](https://pypi.org/project/scratchcloud/)
[![PyPi Downloads / Month](https://img.shields.io/pypi/dm/scratchcloud)](https://pypi.org/project/scratchcloud/)
[![Discord server invite](https://discord.com/api/guilds/963940005837946890/widget.png)](https://discord.gg/K4t2WNnEPC)

## Features
 * Efficient asynchronous connection with Scratch.
 * Event-based handling of cloud variables.
 * Built-in reconnecting.
 * Encoding and decoding support.

## Extensions
 * Fetching data from the Scratch API.
 * Easily customizable codecs for encoding and decoding variables.
 * Sending and parsing large cloud payloads.
 * Validating the cloud by finding who changed a cloud variable.

## Example
```python
from scratchcloud import CloudClient, CloudChange

client = CloudClient('yuwe', '588579111')

@client.event
async def on_connect():
    print('Connected!')

@client.event
async def on_disconnect():
    print('Disconnected!')

@client.event
async def on_message(cloud: CloudChange):
    print(f"{cloud.name} was set to {cloud.value}!")
    await client.set_cloud(cloud.name, "123")

client.run("SuperSecretPassword22")
```

## Links
 * [Docs](https://yuwex.github.io/scratchcloud)
 * [PyPi](https://pypi.org/project/scratchcloud/)
 * [Scratch](https://scratch.mit.edu)