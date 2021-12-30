Basic Tutorial
==============

This tutorial assumes you've already installed ScratchCloud. See :doc:`getting_started` if you haven't yet.

This tutorial will create a basic event-based application.

Basic Events
------------

First, we need to import the ScratchCloud ``CloudClient`` object and create a basic client.

.. code-block:: python
   
   from ScratchCloud import CloudClient

   client = CloudClient(username='yuwe', project_id='588579111')

In this code, we first import the ``CloudClient`` object. Then, using our username and the ID of the project we want to connect to, we create a new ``CloudClient`` object named client. The project id `588579111 <https://scratch.mit.edu/projects/588579111/>`_ is a basic test project.

Next, we're going to specify some events. ScratchCloud uses python decorators to define all event-based interactions.

Add these lines:

.. code-block:: python
   :emphasize-lines: 1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15

   from ScratchCloud import CloudClient, CloudChange

   client = CloudClient(username='yuwe', project_id='588579111')

   @client.event
   async def on_connect():
     print('Hello world!')

   @client.event
   async def on_disconnect():
     print('Goodbye world!')

   @client.event
   async def on_message(var: CloudChange):
     print(f'{var.name} changed to {var.value}!')

These are all the types of ScratchCloud built-in events.

The first thing to notice is the decorators, ``@client.event``. These client event decorators tell your client object to search for specific names. Event functions must use their perscribed names, being ``on_connect``, which is called when the client connects to scratch, ``on_disconnect`` when the client disconnects from scratch, and ``on_message``, when any cloud variable changes in the client's project.

The keyword ``async`` is used before all functions with the ``@client.event`` decorator. Since this library is asynchronous, we must specify that all functions created by the library are async as well.

Lastly, the change to the first line imports the CloudChange object, which is used in the ``on_message`` event. The ``on_message`` variable requires one positional argument, that will always be of type CloudChange. CloudChange objects have several attributes, and we use ``CloudChange.name`` and ``CloudChange.value`` in this code, which represent the name and value of a variable we receieve.

Finally, we just have to run our client. Add this line with your password:

.. code-block:: python
   :emphasize-lines: 17
   
   from ScratchCloud import CloudClient, CloudChange

   client = CloudClient(username='yuwe', project_id='588579111')

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

If we hop over to the `project <https://scratch.mit.edu/projects/588579111/>`_ we connected to, click the cat, and change some variables, our ScratchCloud client will print the changes!

Setting Cloud Variables
-----------------------

Lets change the code a bit to set some variables! Our CloudClient object has a method called ``set_cloud`` we can use to change cloud variables.

Using the previous code, in our ``on_message`` event, lets change a cloud variable:

.. code-block:: python
   :emphasize-lines: 4

   @client.event
   async def on_message(var: CloudChange):
     print(f'{var.name} changed to {var.value}!')
     await client.set_cloud(var.name, '200')

Our ``client.set_cloud`` requires two parameters: the name of the cloud variable we're going to set, and the value we're going to set it to. Using ``var.name`` and ``'200'``, we can "respond" to someone setting a variable by setting it ourselves. We need to include the ``await`` keyword before we set any variables to make sure that our code runs in order and continues to be async.

If we run our client again and send another variable to the `project <https://scratch.mit.edu/projects/588579111/>`__, we will get a response back!

Using Cloud Events
------------------

ScratchCloud has a system for monitoring only a specific cloud variable. This system is cloud events. Cloud events allow programmers to use different cloud variables for different things. They also come with simple error handling.

Let's create a simple cloud event:

.. code-block:: python
   :emphasize-lines: 4, 5, 6, 7

   from ScratchCloud import CloudClient, CloudChange
   client = CloudClient(username='yuwe', project_id='588579111')

   @client.cloud_event('REQUEST')
   async def on_request(var: CloudChange):
     print(f'The REQUEST variable was changed to {var.value}!')
     await client.set_cloud('RESPONSE', '200')
    
   client.run('Your Password Here!')

In this example, we define a simple cloud event. Whevever the cloud variable named ``REQUEST`` changes, the client changes the ``RESPONSE`` cloud variable to 200.

We can also catch errors in cloud events:

.. code-block:: python
   :emphasize-lines: 11, 12, 13, 14, 15, 16

   from ScratchCloud import CloudClient, CloudChange
   client = CloudClient(username='yuwe', project_id='588579111')

   @client.cloud_event('REQUEST')
   async def on_request(var: CloudChange):
     to_divide = int(var.value)
     result = str(100 / to_divide)
     print(f'100 / {to_divide} = {result}')
     await client.set_cloud('RESPONSE', result)
   
   @client.cloud_event_error('REQUEST')
   async def on_request_error(var: CloudChange, error: Exception):
     if isinstance(error, ZeroDivisionError):
       await client.set_cloud('RESPONSE', '0')
     else:
       raise error

   client.run('Your Password Here!')

In this example, we set the response variable to 100 divided by the value the user inputs. If the user enters 0, we catch the ZeroDivisionError, and handle it appropriately.