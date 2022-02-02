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
  
... more here abt parameters of BaseCodec

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

