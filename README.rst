============
Twitchy
============

Twitchy is an easy to use Twitch API wrapper with focus on the Helix API, webhooks, and chat.

.. image:: https://user-images.githubusercontent.com/7674344/100273792-5ae52d00-2f2b-11eb-9710-588aeec63a50.png
   :height: 371
   :width: 507

Requirements
===============

- Python 3.5 or newer
- Twitch API Credentials


Installation
===============

  .. code-block:: bash

    pip install twitchy

Usage
===============

  .. code-block:: python

    from twitchy import Helix

    twitch = Helix(client_id="****", oauth_token="****")

    me = twitch.get_user()

    print(me.id)
    print(me.display_name)

Quickstart
===============
**Authentication**
------------------

In January 2020, Twitch made a change that requires all requests to be accompanied
by a User Access Token or an App Access Token.

To authenticate as a user, provide the OAuth token when instantiating `Helix`.

  .. code-block:: python

    from twitchy import Helix

    twitch = Helix(client_id="****", oauth_token="****")

To authenticate using an `App Access Token`, just provide the Client ID and Client Secret,
and Twitchy will handle authorization for you when necessary.


  .. code-block:: python

    from twitchy import Helix

    twitch = Helix(client_id="****", client_secret="****")

To get a Client ID and Client Secret, register an app on the `Twitch Dev Console`_.


**Making Requests**
-------------------

Methods on the `Helix` class will all be named as obviously as possible by naming them
after the Twitch Helix endpoint they're interfacing with. You can find examples in our examples
folder.

Reference for Twitch Helix endpoints can be found in the `Twitch Helix API documentation`_.


Contributing
===============
Requirements:
-------------

- Commitizen: Commit message consistency.
- pre-commit: For interfacing with pre-commit git hooks.
- Black: Code formatting.
- PyLint: Code linting.

When writing a commit, be sure to use `git commit` without the `-m` to open the commitizen cli.


Steps to Contribute:
---------------------

- Fork the repo and create your branch from **main**.
- If you've added any code that should be tested, add tests.
- If an issue doesn't exist yet, create an issue for tracking purposes.
- Open a Pull Request referencing the issue # in the message body.

If contributing user-facing methods, be sure to use the included `docstringsTemplate` mustache config for docstrings either via
editor extension, or manual process.


Reference Links
---------------
- Twitch Dev Console: https://dev.twitch.tv/
- Twitch Helix API Documentation: https://dev.twitch.tv/docs/api/reference

.. _Twitch Dev Console: https://dev.twitch.tv/
.. _Twitch Helix API Documentation: https://dev.twitch.tv/docs/api/reference
