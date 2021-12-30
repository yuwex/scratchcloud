Getting Started
===============

Welcome to ScratchCloud!

ScratchCloud is a python library for the popular block-based programming language, `Scratch <https://scratch.mit.edu>`_. Scratch has a feature called `cloud variables <https://en.scratch-wiki.info/wiki/Cloud_Data>`_, which are variables that are stored on the cloud, and can be seen and changed by anyone. Cloud variables are not useable by "`New Scratchers <https://en.scratch-wiki.info/wiki/New_Scratcher_Status>`_".

How it works
------------

Scratch cloud variables use a protocol called websockets to transfer their data between scratch users. The websockets set up by the scratch team allow any logged-in user to change the cloud variables of any project, regardless of whether the user owns the project or not. To stop users from using cloud variables in a way the owner of the project didn't originally intend, the scratch website has a failsafe where clicking on the "see-inside" button of a project will terminate its websocket connection.

ScratchCloud uses login information provided by the user to connect to the scratch cloud variable servers. This allows programmers to view and modify cloud variables on any project through python, opening endless possibilities.

ScratchCloud uses the `AIOHttp <https://docs.aiohttp.org/en/stable/>`_ and `Requests <https://docs.python-requests.org/en/latest/>`_ python libraries.

Installation
------------

ScratchCloud is an asynchronous library. It is recommended to have intermediate python, OOP, and asyncio knowledge before using this library.

1. Make sure you have scratcher status by checking scratch.mit.edu/users/your_name/. If you do not have scratcher status, you cannot use this library!
2. Install `python <https://www.python.org/downloads/>`_
3. Use ``pip install ScratchCloud`` (``pip3 install ScratchCloud`` for some mac users) to install ScratchCloud. Virual environments are always recommended!
4. Use ``pip show ScratchCloud`` (``pip3 show ScratchCloud`` for some mac users) to make sure that the installation worked.

Now that you've successfully installed the ScratchCloud package, you can start some actual coding!