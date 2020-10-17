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

twitch = Helix(client_id="**********", oauth_token="*********")

me = twitch.get_user()

print(me.id)
print(me.display_name)

Contributing
===============
