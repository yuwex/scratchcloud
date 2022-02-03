Extensions Tutorial
===================

**This tutorial will explain the different extensions in this library.**

This tutorial assumes you've already installed scratchcloud. See :doc:`getting_started` if you haven't yet.
This tutorial also assumes you've already read :doc:`basic_tutorial`.

Codecs Extension
----------------

Scratch only accepts numbers in its cloud variables. To send non-numeric characters to scratch, an encoder must be used to turn letters into numbers.

scratchcloud has encoder and decoder support built in. The ``encoder`` and ``decoder`` parameters in a CloudClient will automatically encode and decode cloud variables, taking away the overhead of dealing with encoding yourself. These parameters must both be functions that take one argument and return a string.

While scratchcloud allows you to use any encoder you choose, it comes with the built-in codec extension. Currently the only codec is BaseCodec.

BaseCodec is usable out-of-box, after a simple import:

.. code-block:: python

  from scratchcloud import CloudClient
  from scratchcloud.ext import BaseCodec

  codec = BaseCodec()

  client = CloudClient(username='yuwe', project_id='622084628', encoder=codec.encode, decoder=codec.decode)

Then, going to the `BaseCodec Scratch Project <https://scratch.mit.edu/projects/622026587>`_ and backpacking the BaseCodec sprite will allow you to easily send letters between scratch and scratchcloud.

While scratchcloud will automatically encode and decode data, scratch will not. Make sure to use the ``Encode ( )`` block before sending data and the ``Decode ( )`` block before reading cloud data.

.. image:: images/extensions/scratch_encode.png
  :alt: An image of scratch code using the custom Encode block.
  :width: 400
  
The BaseCodec class has several parameters that allow it to work with other scratch codecs. 

.. warning::
  These values should not be changed if you decide to use the `BaseCodec Scratch Project <https://scratch.mit.edu/projects/622026587>`_. You should only change these values if you are adapting a different style of encoding. 

* ``plainalpha`` - the alphabet that will be used. The normal alphabet contains 67 basic characters, but if you wanted to have support for other characters or upercase characters, you could input your own alphabet here.
* ``offset`` - the offset where numbers start. By default, this is 10, meaning the first letter will be encoded to 10 and decoded from 10. Changing this number to 20 would make the first letter start at 20.
* ``force_lowercase`` - this changes all encoded and decoded data to be lowercase. This is useful if you are dealing with user inputs in Python rather than scratch.
* ``places_per_character`` - this is the length of the encoded value of each character. By default, this 2, meaning each encoded character will be a number of length 2, like 10, 22, or 57. If this number was changed to 3, then each encoded character would be a 3-digit number, like 231, 492, or 001. Some codecs require hundreds or thousands of possible letters, and raising this value will increase the total possible characters that can be sent.

For example, say you wanted to use Sid72020123's `ScratchConnect Encoder <https://github.com/Sid72020123/scratchconnect/blob/main/scratchconnect/scEncoder.py>`_. You can do the following:

.. code-block:: python
  
  codec = BaseCodec(
    plainalpha="""BCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ """,
    offset=0,
    force_lowercase=False,
    places_per_character=2,
  )

The BaseCodec documentation can be found here: :class:`scratchcloud.ext.codecs.BaseCodec`

API Connection Extension
------------------------

Some scratch users may want to use the scratch API in their projects. This can be done through the APIConnection extension.

.. code-block:: python
  
  from scratchcloud import CloudClient
  from scratchcloud.ext import APIConnection

  client = CloudClient(username='yuwe', project_id='622084628')
  api = APIConnection(client)

The APIConnection has three basic fetch functions: ``fetch_user()``, ``fetch_project()``, and ``fetch_studio()``.

.. warning::
  Sending more than 10 api requests per second will result in the complete CloudClient being rate limited. Since scratchcloud does not have built in ratelimiting (yet), please be mindful of how many requests you send! This library was made for event-based interactions rather than constant updating.

... more here abt API connection

.. code-block:: python
   
  from scratchcloud import CloudClient

  client = CloudClient(username='yuwe', project_id='622084628')


Utils Extension
---------------

Say what it is

Link to docs

Code example

.. code-block:: python
   
  from scratchcloud import CloudClient

  client = CloudClient(username='yuwe', project_id='622084628')

