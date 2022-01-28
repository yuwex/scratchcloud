Basic Tutorial
==============

**This tutorial will create a basic event-based application.**

This tutorial assumes you've already installed scratchcloud. See :doc:`getting_started` if you haven't yet.

Basic Events
------------

First, create a file ``main.py``:

.. code-block:: python
   
  from scratchcloud import CloudClient

  client = CloudClient(username='yuwe', project_id='622084628')

In this code, we first import the ``CloudClient`` object. Then, using our username and the ID of the project we want to connect to, we create a new ``CloudClient`` object named client. The project id `622084628 <https://scratch.mit.edu/projects/622084628/>`_ is a basic test project.

.. warning::
  ``CloudClient`` objects will only connect to projects that have cloud variables. If a project does not have any cloud variables, a ``MissingCloudVariable`` exception will be raised.

Next, we're going to specify some events. scratchcloud uses python decorators to define all event-based interactions.

.. code-block:: python
  :emphasize-lines: 1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15

  from scratchcloud import CloudClient, CloudChange

  client = CloudClient(username='yuwe', project_id='622084628')

  @client.event
  async def on_connect():
    print('Hello world!')

  @client.event
  async def on_disconnect():
    print('Goodbye world!')

  @client.event
  async def on_message(var: CloudChange):
    print(f'{var.name} changed to {var.value}!')

These are all the types of scratchcloud built-in events.

The first thing to notice is the decorators, ``@client.event``. These client event decorators tell your client object to search for specific names. Event functions must use their perscribed names, being ``on_connect``, which is called when the client connects to scratch, ``on_disconnect`` when the client disconnects from scratch, and ``on_message``, when any cloud variable changes in the client's project.

.. note::
  The keyword ``async`` is used before all functions with the ``@client.event`` decorator. Since this library is asynchronous, many of its methods require the ``async`` keyword.

Lastly, the change to the first line imports the CloudChange object, which is used in the ``on_message`` event. The ``on_message`` variable requires one positional argument, that will always be of type CloudChange. CloudChange objects have several attributes, and we use ``CloudChange.name`` and ``CloudChange.value`` in this code, which represent the name and value of a variable we receieve. The ``on_message`` variable will be called whenever any cloud variable is changed by anyone, excluding the connected CloudClient.

Finally, we just have to run our client. Add this line with your password:

.. code-block:: python
  :emphasize-lines: 17
  
  from scratchcloud import CloudClient, CloudChange

  client = CloudClient(username='yuwe', project_id='622084628')

  @client.event
  async def on_connect():
    print('Hello world!')

  @client.event
  async def on_disconnect():
    print('Goodbye world!')

  @client.event
  async def on_message(var: CloudChange):
    print(f'{var.name} changed to {var.value}!')

  client.run('Your Password Here!')

The text that states ``'Your Password Here!'`` should be your actual password. The ``client.run`` method is the only blocking function in the library.

If we hop over to the `project <https://scratch.mit.edu/projects/622084628/>`_ we connected to, click the cat, and change some variables, our scratchcloud client will print the changes!

.. note::
  
  You can stop a ``CloudClient`` by using Control + C.

Setting Cloud Variables
-----------------------

Lets change the code a bit to set some variables! Our CloudClient object has a method called ``set_cloud`` we can use to change cloud variables.

Using the previous code, in our ``on_message`` event, lets change a cloud variable:

.. code-block:: python
  :emphasize-lines: 16
   
  from scratchcloud import CloudClient, CloudChange

  client = CloudClient(username='yuwe', project_id='622084628')

  @client.event
  async def on_connect():
    print('Hello world!')

  @client.event
  async def on_disconnect():
    print('Goodbye world!')

  @client.event
  async def on_message(var: CloudChange):
    print(f'{var.name} changed to {var.value}!')
    await client.set_cloud(var.name, '200')
  
  client.run('Your Password Here!')

Our ``client.set_cloud`` method requires two parameters: the name of the cloud variable we're going to set, and the value we're going to set it to. Using ``var.name`` and ``'200'``, we can "respond" to someone setting a variable by setting it back to 200. We need to include the ``await`` keyword before we set any variables to make sure that our code runs in order and continues to be async.

If we run our client again and send another variable to the `project <https://scratch.mit.edu/projects/622084628/>`__, the variable we set will immediately be reset to 200!

Using Cloud Events
------------------

scratchcloud has a system for monitoring only a specific cloud variable. This system is cloud events. Cloud events allow programmers to use different cloud variables for different things. They also come with simple error handling.

Let's rewrite ``main.py`` with the following:

.. code-block:: python
  :emphasize-lines: 12, 13, 14, 15

  from scratchcloud import CloudClient, CloudChange
  client = CloudClient(username='yuwe', project_id='622084628')

  @client.event
  async def on_connect():
    print('Hello world!')

  @client.event
  async def on_disconnect():
    print('Goodbye world!')

  @client.cloud_event('REQUEST')
  async def on_request(var: CloudChange):
    print(f'The REQUEST variable was changed to {var.value}!')
    await client.set_cloud('RESPONSE', '200')
  
  client.run('Your Password Here!')

In this example, we define a simple cloud event. Whevever the cloud variable named ``REQUEST`` changes, the client changes the ``RESPONSE`` cloud variable to 200.
This style of call and response coding is very efficient and is recommended in writing your own code.

.. note::
  In this example, in scratch, the cloud variables are named ``☁️ REQUEST`` and ``☁️ RESPONSE``.
  Make sure that in your own code, for `client.cloud_event` and `client.set_cloud`, you use the correct variable names without the cloud emoji! 
  If your variable was named ``☁️ Cloud Data`` in scratch, it would be called ``Cloud Data`` in scratchcloud.

Lets say, for some reason, receiving a 0 from a user causes an error in your code.

scratchcloud makes it easy to catch errors in cloud events. In the same program change the `cloud_event` function to raise an ``Exception`` and add the following ``@client.cloud_event_error``:
Cloud event error decorators are set up in the similarly to ``@client.cloud_event``, but they have an extra positional argument for the raised error.

.. code-block:: python
  :emphasize-lines: 15, 16, 19, 20, 21, 22, 23

  from scratchcloud import CloudClient, CloudChange
  client = CloudClient(username='yuwe', project_id='622084628')

  @client.event
  async def on_connect():
    print('Hello world!')

  @client.event
  async def on_disconnect():
    print('Goodbye world!')

  @client.cloud_event('REQUEST')
  async def on_request(var: CloudChange):
    print(f'The REQUEST variable was changed to {var.value}!')
    if var.value == '0': # Raise an error whenever we get 0!
      raise ValueError('Zeros are bad!')
    await client.set_cloud('RESPONSE', '200')

  @client.cloud_event_error('REQUEST')
  async def on_request_error(var: CloudChange, error: Exception):
  if isinstance(error, ValueError):
    await client.set_cloud('RESPONSE', '400') # Set the response to 400 if something goes wrong!
  else:
    raise error

  client.run('Your Password Here!')

In this example, whenever we receieve the number 0, an exception is raised. After the exception is raised, it's caught by the ``@client.cloud_event_error`` function, and handled appropriately through Python's ``isinstance`` function.
