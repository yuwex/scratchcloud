Examples
============

Example 1: Ping Pong
--------------------

In this example, when someone sends a "ping", scratchcloud will send back a "pong".

This example is linked to the project `622779749 <https://scratch.mit.edu/projects/622779749/>`__.

.. code-block:: python
    :emphasize-lines: 1, 3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 18
    :linenos:

    from scratchcloud import CloudClient, CloudChange

    client = CloudClient(username='yuwe', project_id='622779749')

    @client.event
    async def on_connect():
        print('Started!')

    @client.event
    async def on_disconnect():
        print('Stopped!')

    @client.cloud_event('REQUEST')
    async def on_request(cloud: CloudChange):
        print(f'Got ping value of {cloud.value}. Sending pong...')
        await client.set_cloud('RESPONSE', cloud.value)

    client.run('password')

Description:

* Line 1: Imports scratchcloud
* Line 3: Creates a new ``CloudClient`` object
* Line 5-11: Sets up print statements when connected and disconnected
* Line 13-14: Sets up a cloud event function for the cloud variable ``REQUEST``. This is called whenever ``REQUEST`` is set in scratch
* Line 16: Sets the ``RESPONSE`` cloud variable to the value of the ``REQUEST`` variable
* Line 18: Run the ``CloudClient`` object

Example 2: Hex Hash
-------------------

In this example, when someone sends data, scratchcloud `hashes <https://en.wikipedia.org/wiki/Hash_function>`__ it.

This example is linked to the project `622792569 <https://scratch.mit.edu/projects/622792569/>`__.


.. code-block:: python
    :emphasize-lines: 2, 3, 5, 7, 19, 20, 23, 25, 26, 27, 28, 29, 30, 31, 32
    :linenos:

    from scratchcloud import CloudClient, CloudChange
    from scratchcloud.ext import BaseCodec
    from scratchcloud.errors import DecodeError, SizeError

    from hashlib import md5

    client = CloudClient(username='yuwe', project_id='622792569', encoder=BaseCodec().encode, decoder=BaseCodec().decode)

    @client.event
    async def on_connect():
        print('Connected!')
        
    @client.event
    async def on_disconnect():
        print('Disconnected!')

    @client.cloud_event('REQUEST')
    async def on_request(cloud: CloudChange):
        hashed_result = md5(cloud.value.encode())
        hex_result = hashed_result.hexdigest()
        print(f'Got {cloud.value}. Hashing to {hex_result}...')

        await client.set_cloud('RESPONSE', f'The MD5 hash for \"{cloud.value}\" is {hex_result}')

    @client.cloud_event_error('REQUEST')
    async def request_error(error: Exception, cloud: CloudChange):
        if isinstance(error, DecodeError):
            await client.set_cloud('RESPONSE', 'there was an error decoding your data')
        elif isinstance(error, SizeError):
            await client.set_cloud('RESPONSE', 'the response was too long to be sent')
        else:
            raise error

    client.run('password')

Description:

* Line 2: Imports ``BaseCodec``, which will be used for encoding/decoding all data. This allows us to send letters instead of numbers
* Line 3: Imports some errors that will be used later.
* Line 5: Imports the builtin python md5 hash function
* Line 7: Creates a ``CloudClient`` object with  ``encoder=BaseCodec().encode`` and ``decoder=BaseCodec().decode``, specifing our encoding and decoding method.
* Lines 19-20: Hashes the value received from the ``REQUEST`` variable
* Line 23: Sends the hashed result. A non-digit value can be used because a encoder was specified when creating the ``CloudClient``
* Lines 25-26: Sets up a cloud event error function for the cloud variable ``REQUEST``. This is called whenever an error is raised in the cloud event ``REQUEST`` function
* Lines 27-32: Handle errors and send error messages

Example 3: API Users
--------------------

In this example, when someone sends a scratch username, scratchcloud responds with that user's information.

This example is linked to the project `622799182 <https://scratch.mit.edu/projects/622799182/>`__.

.. code-block:: python
    :emphasize-lines: 2, 6, 20, 21, 22, 23, 24, 26, 27, 28
    :linenos:

    from scratchcloud import CloudClient, CloudChange
    from scratchcloud.ext import BaseCodec, APIConnection
    from scratchcloud.errors import DecodeError, NotFoundError, SizeError

    client = CloudClient(username='yuwe', project_id='622799182', encoder=BaseCodec().encode, decoder=BaseCodec().decode)
    api = APIConnection(client)

    @client.event
    async def on_connect():
        print('Connected!')

    @client.event
    async def on_disconnect():
        print('Disconnected!')

    @client.cloud_event('REQUEST')
    async def on_request(cloud: CloudChange):
        print(f'Request for user \"{cloud.value}\" received!')

        try:
            user = await api.fetch_user(cloud.value)
        except NotFoundError:
            await client.set_cloud('RESPONSE', f'the user \"{cloud.value}\" could not be found.')
            return

        username = user.name
        country = user.country
        join_date = user.joined_at.strftime('%B %d, %Y')

        await client.set_cloud('RESPONSE', f'i\'m {username} from {country}! I joined on {join_date}')

    @client.cloud_event_error('REQUEST')
    async def request_error(cloud: CloudChange, error: Exception):
        if isinstance(error, DecodeError):
            await client.set_cloud('RESPONSE', 'there was an error decoding your data.')

        elif isinstance(error, SizeError):
            await client.set_cloud('RESPONSE', 'the response was too long to be sent.')

        else:
            raise error

    client.run('password')

Description:

* Line 2: Imports ``BaseCodec`` and ``APIConnection``. An ``APIConnection`` object can get scratch user information
* Line 6: Creates a new APIConnection object
* Line 21: Fetches a user object using the APIConnection
* Lines 20-24: Checks to see if there is an issue with fetching a user. If there is, set the ``RESPONSE`` cloud variable to an error message and exit
* Lines 26, 27, 28: Sets ``username``, ``country``, and ``join_date`` variables from the ``User`` object
