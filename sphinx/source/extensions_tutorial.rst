Extensions Tutorial
===================

**This tutorial will explain the different extensions in this library.**

This tutorial assumes you've already installed scratchcloud. See :doc:`getting_started` if you haven't yet.
This tutorial also assumes you've already read :doc:`basic_tutorial`.

Codecs Extension
----------------

Scratch only accepts numbers in its cloud variables. To send non-numeric characters to scratch, an encoder must be used to turn letters into numbers.

Sending non-numeric characters is built into scratchcloud through encoders and decoders. The ``encoder`` and ``decoder`` parameters in a CloudClient will automatically encode and decode cloud variables. These parameters must both be functions that take one argument and return a string.

While scratchcloud allows you to use any function as an encoder or decoder, it comes with the built-in codec extension. Currently the only codec is BaseCodec.

BaseCodec is usable out-of-box, after a simple import:

.. code-block:: python
  :linenos:
  :emphasize-lines: 2, 4, 6

  from scratchcloud import CloudClient, CloudChange
  from scratchcloud.ext import BaseCodec

  codec = BaseCodec()

  client = CloudClient(username='yuwe', project_id='622084628', encoder=codec.encode, decoder=codec.decode)

  @client.event
  async def on_message(cloud: CloudChange):
    print(f'{cloud.name} changed to {cloud.value}')


* Line 2 imports scratchcloud's built in codec system.
* Line 4 creates a new BaseCodec object.
* Line 6 creates a CloudClient with the encoder and decoder parameters from the BaseCodec object.

Connecting to the `scratchcloud Test Interface <https://scratch.mit.edu/projects/622084628>`_ in scratch and switching the "Encode Request" slider to 1 will encode everything you send from it. If you run the above code, you should now be able to get non-numeric characters in scratchcloud!

Going to the `BaseCodec Scratch Project <https://scratch.mit.edu/projects/622026587>`_ and backpacking the BaseCodec sprite will allow you to easily send letters between scratch and scratchcloud in your own projects.

While scratchcloud will automatically encodes and decodes data, scratch will not. Make sure to use the ``Encode ( )`` block and the "➡️ encoded" varible before setting any cloud variables and the ``Decode ( )`` and "➡️ decoded" varible block before reading cloud variables.

.. image:: images/extensions/scratch_encode.png
  :alt: An image of scratch code using the custom Encode block.
  :width: 400
  
The BaseCodec class has several parameters that allow it to work with other scratch codecs. 

* ``plainalpha`` - the alphabet that will be used. The normal alphabet contains 67 basic characters and does not support uppercase letters. If you wanted to have support for other characters or upercase letters, you could input your own alphabet here.
* ``offset`` - the offset where numbers start. By default, this is 10, meaning the first letter will be encoded to 10 and decoded from 10. Changing this number to 20 would make the first letter start at 20.
* ``force_lowercase`` - this changes all encoded and decoded data to be lowercase. This is useful if your data is case-insensitive.
* ``places_per_character`` - this is the length of the encoded value of each character. By default, this 2, meaning each encoded character will be a 2-digit number, like 10, 22, or 57. If this number was changed to 3, then each encoded character would be a 3-digit number, like 231, 492, or 001. Some codecs require hundreds or thousands of possible letters, and raising this value will increase the total possible characters that can be sent.

.. warning::
  These values should not be changed if you decide to use the `BaseCodec Scratch Project <https://scratch.mit.edu/projects/622026587>`_. You should only change these values if you are adapting a different style of encoding. 

For example, say you wanted to use Sid72020123's `ScratchConnect Encoder <https://github.com/Sid72020123/scratchconnect/blob/main/scratchconnect/scEncoder.py>`_. You can do this with the following code:

.. code-block:: python
  
  codec = BaseCodec(
    plainalpha="""ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ """, # The plaintext alphabet that Sid's codec uses
    offset=1, # Sid's codec starts at 1
    force_lowercase=False, # Sid's codec supports uppercase letters
    places_per_character=2, # All encodings in Sid's codec are 2 characters long
  )

The BaseCodec documentation can be found here: :class:`scratchcloud.ext.codecs.BaseCodec`

API Connection Extension
------------------------

Some developers may want to use the scratch API in their projects. This can be done through the APIConnection extension.

The APIConnection class takes a CloudClient as their argument:

.. code-block:: python
  
  from scratchcloud import CloudClient
  from scratchcloud.ext import APIConnection

  client = CloudClient(username='yuwe', project_id='622084628')
  api = APIConnection(client)

The APIConnection has three basic fetch functions: ``fetch_user()``, ``fetch_project()``, and ``fetch_studio()``.

.. warning::
  Fetching the API more than 10 times per second will result in the CloudClient being rate limited. Since scratchcloud does not have built in ratelimiting (yet), please be mindful of how many requests you send! This library was made for event-based interactions rather than constant updating.

* ``fetch_user()`` returns a :class:`scratchcloud.ext.api.User` class
* ``fetch_project()`` returns a :class:`scratchcloud.ext.api.Project` class
* ``fetch_studio()`` returns a :class:`scratchcloud.ext.api.Studio` class

Sending fetch requests is as follows:

.. code-block:: python
  :linenos:
  :emphasize-lines: 9, 10
  
  from scratchcloud import CloudClient, CloudChange
  from scratchcloud.ext import APIConnection

  client = CloudClient(username='yuwe', project_id='622084628')
  api = APIConnection(client)

  @client.event
  async def on_connect():
    user = await api.fetch_user('yuwe')
    print(f'{user.username} is from {user.country}')

Line 9 uses the :meth:`api.fetch_user()` method to get data for the user yuwe and turn it into a user object. Line 10 prints the user's username and the country they're from.

Most objects have extra fetch methods. For example, the Studio class has the methods :meth:`fetch_curators` and :meth:`fetch_managers`.

The APIConnection class will not be updated to contain site-api methods or webscraping. It is solely used for scratch's built in API.

The APIConnection documentation and all of its classes and methods can be found here: :class:`scratchcloud.ext.api`

Utils Extension
---------------

scratchcloud has some utilities that are useful for repetitive or complicated tasks.

SegmentDump Utility
-------------------

The first utility is SegmentDump, which is used to send data that does not fit in scratch's 256-character cloud variable limit.

SegmentDump will break down data into segments with lengths of 256 and set multiple cloud variables to these segments. It can also combine multiple cloud variables into a single piece of data.

.. code-block:: python
  :linenos:
  :emphasize-lines: 2, 6-16, 18
   
  from scratchcloud import CloudClient
  from scratchcloud.ext.utils import SegmentDump

  client = CloudClient(username='yuwe', project_id='650134344')
  
  segments = [
    'Segment 1',
    'Segment 2',
    'Segment 3',
    'Segment 4',
    'Segment 5',
    'Segment 6',
    'Segment 7',
    'Segment 8',
    'Segment 9',
  ]

  segmenter = SegmentDump(client, segments)

A SegmentDump object has two parameters: a CloudClient and a list of cloud variable names.

Line 2 imports SegmentDump. Line 6-16 creates a list of cloud variable names, in this case named Segment 1 - 9. Line 18 creates a SegmentDump object that is linked to the client with said variables.

The SegmentDump object can now be used to split data into multiple variables or read data from multiple variables.

.. code-block:: python
  :linenos:
  :emphasize-lines: 6, 17
   
  from scratchcloud import CloudClient
  from scratchcloud.ext.utils import SegmentDump

  client = CloudClient(username='yuwe', project_id='650134344')
  
  pi = "31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461284756482337867831652712019091456485669234603486104543266482133936072602491412737245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094330572703657595919530921861173819326117931051185480744623799627495673518857527248912279381830119491298336733624406566430860213949463952247371907021798609437027705392171762931767523846748184676694051320005681271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235420199561121290219608640344181598136297747713099605187072113499999983729780499510597317328160963185950244594553469083026425223082533446850352619311881710100031378387528865875332083814206171776691473035982534904287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989"

  segments = [
    'Segment 1', 'Segment 2', 'Segment 3', 'Segment 4', 'Segment 5', 'Segment 6', 'Segment 7', 'Segment 8', 'Segment 9',
  ]

  segmenter = SegmentDump(client, segments)

  @client.event
  async def on_connect():
    print('Setting cloud variables to pi...')
    await segmenter.dump(pi)

In the example above, line 6 is the first 1000 digits of pi. Then, the :meth:`dump` method is used to set multiple cloud variables to parts of Pi. All variables that do not contain any part of pi are set to "0".

Here is what SegmentDump does internally:

#. The "Segment 1" variable is set to the first 256 digits of pi.
#. The "Segment 2" variable is set to the next 256 digits of pi.
#. The "Segment 3" variable is set to the next 256 digits of pi.
#. The "Segment 4" variable is set to the remaining 232 digits of pi.
#. The "Segment 5" through "Segment 9" variables are set to the default ``empty_value`` of "0".

You can change what the empty value with the ``empty_value`` argument:

.. code-block:: python
  
  await segmenter.dump(pi, empty_value='22')

SegmentDump reads a client's encode and decode functions. If an encoder/decoder is specified, you may specify if a SegmentDump object uses them:

.. code-block:: python

  from scratchcloud import CloudClient
  from scratchcloud.ext.utils import SegmentDump
  from scratchcloud.codecs import BaseCodec

  codec = BaseCodec(force_lowercase = True)

  # Set an encoder and decoder using BaseCodec
  client = CloudClient(username='yuwe', project_id='650134344', encoder=codec.encode, decoder=codec.decode)

  text_to_send = "Lorem ipsum dolor sit amet, consectetaur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

  @client.event
  async def on_connect():
    print('Setting cloud variables to text...')
    # Encode the data to send and the empty variable value using the client's encoder and decoder parameters
    await segmenter.dump(text_to_send, encode_data = True, empty_value='unset', encode_empty = True)

The SegmentDump documentation and all of its classes and methods can be found here: :class:`scratchcloud.ext.utils.SegmentDump`

CloudValidator Utility
----------------------

The second utility is the CloudValidator. 

Often, developers will want to validate that a specific user is who they claim to be. Lots of cloud servers will simply send a username from Scratch, but this is unsafe because anyone can use a cloud variable library to fake their identity. The CloudValidator fixes this issue by finding the user that sent a CloudChange object through the cloud api.

The CloudValidator is simple to use. Simply create a new CloudValidator with a CloudClient object as a parameter, and use the :meth:`validate_cloud` method on a CloudChange object:

.. code-block:: python

  from scratchcloud import CloudClient
  from scratchcloud.ext.utils import CloudValidator

  client = CloudClient(username='yuwe', project_id='622084628')

  validator = CloudValidator(client)

  @client.event
  async def on_message(cloud: CloudChange):
    sender = validator.validate_cloud(cloud)

    print(f'{cloud.name} changed to {cloud.value} by {sender}')

.. warning ::
  The CloudValidator CAN be ratelimited, so please minimize your use. Don't validate variables that are constantly updated: this will result in your entire client getting disconnected.

If the CloudValidator fails in its validation, a :class:`UnableToValidate` exception will be raised. This can be caught at the call location, or using ``on_message_error`` or ``on_cloud_event_error`` decorated functions.

The CloudValidator documentation and all of its classes and methods can be found here: :class:`scratchcloud.ext.utils.CloudValidator`