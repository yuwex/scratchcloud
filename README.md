# scratchcloudpy
An asynchronous Pythonic wrapper for scratch.mit.edu cloud variables.

## Features
 * Event-based handling
 * Pythonic `async` and `await` syntax
 * Built-in reconnecting

## Example
```python
from scratchcloudpy.client import CloudClient, CloudChange

client = CloudClient('SS-2', '588579111')

@client.event
async def on_connect():
    print('Connected!')

@client.event
async def on_disconnect():
    print('Disconnected :(')

@client.event
async def on_message(cloud: CloudChange):
    print(f"I got: {cloud}!")
    await client.set_cloud(cloud.name, "123")

client.run("SuperSecretPassword22")
```

## Links
 * [Scratch](https://scratch.mit.edu)
 * [Python Asyncio](https://docs.python.org/3/library/asyncio.html)