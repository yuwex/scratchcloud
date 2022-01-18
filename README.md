# scratchcloud
An asynchronous pythonic wrapper for scratch.mit.edu cloud websocket connections.

## Features
 * Event-based handling
 * Pythonic `async` and `await` syntax
 * Built-in reconnecting

## Extensions
 * Fetching data from the Scratch API
 * Easy encoding and decoding of variables
 * Sending and receiving large cloud payloads
 * Finding who changed a cloud variable
gt
## Example
```python
from scratchcloud import CloudClient, CloudChange

client = CloudClient('SS-2', '588579111')

@client.event
async def on_connect():
    print('Connected!')

@client.event
async def on_disconnect():
    print('Disconnected :(')

@client.event
async def on_message(cloud: CloudChange):
    print(f"{cloud.name} was set to {cloud.value}!")
    await client.set_cloud(cloud.name, "123")

client.run("SuperSecretPassword22")
```

## Links
 * [Docs](https://yuwex.github.io/scratchcloud)
 * [Scratch](https://scratch.mit.edu)
 * [Python Asyncio](https://docs.python.org/3/library/asyncio.html)