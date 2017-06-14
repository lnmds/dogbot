# `dogbot`

![fuyu approved](https://img.shields.io/badge/fuyu-approved-green.svg)

Dogbot is my personal Discord bot that I use on my servers. It has no real
purpose, it just has handy commands that I like to use! Some serve
administrative or utility purposes, and some are just for fun!

Dogbot is currently undergoing steady development. I try to add new features
everyday, so please bear with me and submit feedback if something goes wrong!

## Uptime and disclaimer

I try to keep Dogbot running 24/7. However, please don't complain when the bot
goes down or disappears entirely! I am a busy person, and I apologize ahead of
time if the bot causes trouble due to it being down or misbehaving.

I am not responsible for any damages caused by Dogbot. Don't worry though,
Dogbot never purposely causes any damages to your server unless I have made a
mistake somewhere. If it does, please report it to me as feedback (see above).

## Contributing

I love contributions! Please send me them by opening a pull request or by
opening an issue if you notice something.

## Running your own

I heavily prefer that you [invite Dogbot to your server](https://discordapp.com/oauth2/authorize?permissions=402730176&scope=bot&client_id=295770389584412683) instead of running your instance of Dogbot.

However, if you really want to run Dogbot yourself, follow the instructions below:

### Requirements

- Python 3.6 (not 3.5 or below)
- Required Python modules (check `requirements.txt`, run `pip install -r requirements.txt`)
- Redis
- Postgresql

### Configuration

Create a `dog_config.py` file in the root of the repository.

```py
# auth
token = '<your token...>'
owner_id = <your id...>

# db
redis_url = 'localhost'
postgresql_auth = {
  'user': '...',
  'password': '...',
  'database': 'dogbot',
  'host': '127.0.0.1'
}

# third party auth
myanimelist = {
  'username': '...',
  'password': '...'
}
owm_key = '' # open weather map
oxford_creds = { # oxford dictionaries
    'application_id': '',
    'application_key': ''
}

# reporting
raven_client_url = '<sentry auth url>'  # (or empty string)
discordpw_token = '<bots.discord.pw api token>'  # (optional)
reddit = {
    'client_id': '',
    'client_secret': '',
    'user_agent': 'discord:...:v1.0.0 (by /u/...)'
}

# cfg
prefixes = ['dog, ', 'd?']
github = '<your github username>/<repository name>'
```

Specify your token and prefixes.

Note that some variables in the bot are hardcoded in and are not configurable.
Please look for these occurrences in the code and replace them if applicable.

I try to keep the code as readable as possible!

### Optional packages

 - `uvloop`: Install this for possibly faster `asyncio`! Windows is not
   supported.

### Running

When you're done configuring, start `dog.py`.

### Deployment

An Ansible playbook and systemd unit is included in this repository. All of the files are copied to `/srv/dog`. Make sure this directory exists before attempting to run the playbook.

#### Usage

Keep a `dog_config.production.py` file in the repository. This will be copied to the remote server by the Playbook.

#### Playbook

The playbook does the following:

1. Ensure that Postgresql and Redis are installed
2. Ensure that both services are running and enabled
3. Ensure that the Postgres database (`dogbot`) exists
4. Clone the source code from GitHub
    1. The database tables defined in `schema.sql` are created if needed
5. Copy the configuration file to the server (`dog_config.production.py`)
6. Install `libmagickwand-dev` (required by Wand) and install required Python packages from `requirements.txt`
7. Install the systemd unit, and restart it
    1. The systemd daemon is reloaded if the unit has changed
