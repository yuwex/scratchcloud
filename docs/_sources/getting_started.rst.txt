Getting Started
===============

Welcome to scratchcloud!

scratchcloud is a python library for the popular block-based programming language, `Scratch <https://scratch.mit.edu>`_. Scratch has a feature called `cloud variables <https://en.scratch-wiki.info/wiki/Cloud_Data>`_, which are variables that are stored on the cloud, and can be seen and changed by anyone.

How it works
------------

Scratch cloud variables use a protocol called websockets to transfer their data between scratch users. The websockets set up by the scratch team allow any logged-in user to change the cloud variables of any project, regardless of whether the user owns the project or not. To stop users from using cloud variables in a way the owner of the project didn't originally intend, the scratch website has a failsafe where clicking on the "see-inside" button of a project will terminate its websocket connection.

Since scratchcloud uses login information provided by the user to connect to the scratch cloud variable servers, it does not have the same failsafe. This allows programmers to view and modify cloud variables on any project through python, opening endless possibilities.

scratchcloud uses the `AIOHttp <https://docs.aiohttp.org/en/stable/>`_ and `websockets <https://websockets.readthedocs.io/en/stable/>`_ python libraries.

Installation
------------

**scratchcloud is an asynchronous library. It is recommended to have intermediate python, object oriented programming, and asyncio knowledge before using this library.**

1. If you don't already have a scratch account, create one `here <https://scratch.mit.edu/join>`_.
2. Install `Python <https://www.python.org/downloads/>`_. scratchcloud requires a version of python larger or equal to 3.10. If you're using Windows, make sure to add python to PATH.
3. Open a command line interface. On Mac, this is Terminal. On Windows, this is usually Command Prompt.
4. Run ``pip install scratchcloud`` to install scratchcloud. Virtual environments are always recommended!

.. note::
    Some users may need to use ``python3 -m pip install scratchcloud`` instead of ``pip install scratchcloud``.

Now that you've successfully installed the scratchcloud package, you can start some actual coding!