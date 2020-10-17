============
PyTwitch
============

PyTwitch is an easy to use Twitch API wrapper with focus on the Helix API, webhooks, and chat.

.. image:: https://user-images.githubusercontent.com/7674344/96326749-5f035e00-1001-11eb-8e55-6ff41e53b074.png
   :height: 371
   :width: 507

Requirements
===============

- Python 3.5 or newer
- A Twitch application
- Twitch OAuth Token for chat

Installation
===============
pip install <package-not-yet-published>

Usage
===============

  .. code-block:: python

    from pytwitch import Helix

    twitch = Helix(client_id="****", oauth_token="****")

    me = twitch.get_user()

    print(me.id)
    print(me.display_name)


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
------------------

- Fork the repo and create your branch from **main**.
- If you've added any code that should be tested, add tests.
- If you've changed APIs or methods that change usage, update documentation.
- If an issue doesn't exist yet, create an issue.
- Open a Pull Request referencing the issue # in the message body.
