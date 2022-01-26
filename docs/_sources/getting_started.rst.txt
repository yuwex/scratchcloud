Getting Started
===============

Welcome to scratchcloud!

scratchcloud is a python library for the popular block-based programming language, `Scratch <https://scratch.mit.edu>`_. Scratch has a feature called `cloud variables <https://en.scratch-wiki.info/wiki/Cloud_Data>`_, which are variables that are stored on the cloud, and can be seen and changed by anyone. Cloud variables are not useable by "`New Scratchers <https://en.scratch-wiki.info/wiki/New_Scratcher_Status>`_".

How it works
------------

Scratch cloud variables use a protocol called websockets to transfer their data between scratch users. The websockets set up by the scratch team allow any logged-in user to change the cloud variables of any project, regardless of whether the user owns the project or not. To stop users from using cloud variables in a way the owner of the project didn't originally intend, the scratch website has a failsafe where clicking on the "see-inside" button of a project will terminate its websocket connection.

scratchcloud uses login information provided by the user to connect to the scratch cloud variable servers. This allows programmers to view and modify cloud variables on any project through python, opening endless possibilities.

scratchcloud uses the `AIOHttp <https://docs.aiohttp.org/en/stable/>`_ and `websockets <https://websockets.readthedocs.io/en/stable/>`_ python libraries.

Installation
------------

.. note::
    scratchcloud is an asynchronous library. It is recommended to have intermediate python, OOP, and asyncio knowledge before using this library.

1. Make sure you have scratcher status by checking scratch.mit.edu/users/your_name/. If you do not have scratcher status, you cannot use this library!
2. Install `python <https://www.python.org/downloads/>`_
3. Use ``pip install scratchcloud`` (``pip3 install scratchcloud`` for some mac users) to install scratchcloud. Virual environments are always recommended!
4. Use ``pip show scratchcloud`` (``pip3 show scratchcloud`` for some mac users) to make sure that the installation worked.

Now that you've successfully installed the scratchcloud package, you can start some actual coding!