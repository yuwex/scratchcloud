Basic Tutorial
==============

**This tutorial will create a basic event-based application.**

This tutorial assumes you've already installed scratchcloud. See :doc:`getting_started` if you haven't yet.

Basic Events
------------

To start off, let's create a basic ``CloudClient``.

.. note:: 
  A ``CloudClient`` is an object that represents the connection between scratch and python. One can be created through the following:

First, create a file named ``main.py``:

.. code-block:: python
   
  from scratchcloud import CloudClient

  client = CloudClient(username='yuwe', project_id='622084628')

In this example, the ``CloudClient`` object is imported. Then, a new ``CloudClient`` object is created using using a username and a project ID. The project id `622084628 <https://scratch.mit.edu/projects/622084628/>`_ is a basic test project for this library.

.. warning::
  ``CloudClient`` objects will only connect to projects that have cloud variables. If a project does not have any cloud variables, a ``MissingCloudVariable`` exception will be raised.

The following code shows how to create events. scratchcloud uses python decorators to define all event-based API interactions.

.. code-block:: python
  :emphasize-lines: 1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17
  :linenos:

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

The first thing to notice are the decorators, ``@client.event``. These client event decorators will call their decorated functions depending on the functions' specific names.

.. warning::
  The keyword ``async`` is used before all functions with the ``@client.event`` decorator. Since this library is asynchronous, all of its API-related methods require the ``async`` keyword.

These function names are:

* ``on_connect`` — Called when the client connects to scratch
* ``on_disconnect`` — Called when the client disconnects from scratch
* ``on_message`` — Called when any cloud variable changes

.. note::
  The ``on_message`` event has special syntax. It requires one positional argument, which is a ``CloudChange`` object. On line 1, ``CloudChange`` is imported.

Whenever a variable changes, the client will create a ``CloudChange`` object with the changed variable information. Then, the client will call the ``on_message`` function with that ``CloudChange`` object.

``CloudChange`` objects have several attributes, and this example uses ``CloudChange.name`` and ``CloudChange.value``.

More attributes for CloudChange objects can be found here: :class:`scratchcloud.client.CloudChange`

Lastly, on line 17, this example runs the code using :meth:`client.run`. The text that states ``'Your Password Here!'`` should be your actual password. The ``client.run`` method is blocking, and all code after it will not be run until the client is stopped.

.. warning::
  If you plan to publish your project on Github or Repl, **make sure that your password is hidden**!
  
  If you want to use Repl to host your projects, check out the ``LoginCookie`` documentation here: :class:`scratchcloud.client.LoginCookie`

After this code is run, going to the `project id <https://scratch.mit.edu/projects/622084628/>`_ specified in the client, clicking the cat, and changing some variables will cause the scratchcloud client to print the changes! For example, clicking the cat and entering 100 will make scratchcloud print ``REQUEST changed to 100!``

.. note::
  
  You can stop a ``CloudClient`` by using Control + C.

Setting Cloud Variables
-----------------------

scratchcloud can also change variables! The ``CloudClient`` object has a method called ``set_cloud`` which can be used to set cloud variables.

Using the previous code, the ``on_message`` event is changed to "respond":

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

The ``client.set_cloud`` method requires two parameters: the name of the cloud variable to be set, and the value the variable will be set to. Using ``var.name`` and ``'200'``, this code "responds" to someone setting a variable by setting it back to 200. Once again, the ``await`` keyword is necesary before setting any variables to ensure asynchronous execution.

If the client is run again, after another variable is sent to the `test project <https://scratch.mit.edu/projects/622084628/>`__, the variable we set will immediately be reset to 200 by the client!

.. warning::
  Spamming ``client.set_cloud`` in a while loop will result in ratelimits and possible account IP bans. The likelyhood of this happening is reduced when using events to "respond" to people "requesting" something!

Using Cloud Events
------------------

scratchcloud has a system for monitoring only a specific cloud variable. This system is cloud events. Cloud events allow programmers to use different cloud variables for different things. They also come with simple error handling.

The following will rewrite ``main.py`` with cloud events:

.. code-block:: python
  :emphasize-lines: 12, 13, 14, 15
  :linenos:

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

In this example, a simple cloud event is defined.

#. First, on line 12, the cloud event decorator is created with a variable name, which, in this case, is ``REQUEST``.
#. On line 13, a async function is defined with one argument of type ``CloudChange``. This function can have any name, but it is recommended to use ``on_variablename`` syntax.
#. Line 14 prints out the changes to the REQUEST cloud variable.
#. Line 15 sets a different variable named ``RESPONSE`` to 200.

This call-and-response method is highly efficient compared to other scratch libraries. There is no polling involved in the internal code, meaning that the client's response is as fast as the websocket connection can be!

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
