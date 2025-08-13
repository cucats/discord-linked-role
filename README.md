# Discord Cambridge Linked Role

Verifies University of Cambridge members via Microsoft Entra ID with the University Central Directory for Discord applications.

## Prerequisites

Obtain a Client ID, Client Secret, and Bot token from https://discord.com/developers/applications
Obtain a Client ID and Client Secret from https://toolkit.uis.cam.ac.uk/endpoints

## Setup

```conf
Environment:
HOST=http://localhost:5000

DISCORD_BOT_TOKEN=
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=

UCAM_CLIENT_ID=
UCAM_CLIENT_SECRET=

FLASK_SECRET=
```

Install dependencies:

```sh
uv sync
```

Register metadata with Discord:

```sh
uv run python -m src.discord`
```

Run a development server:

```sh
uv run python -m src.app
```

Run a production server:

```sh
uv run gunicorn wsgi:app -b "0.0.0.0:5000" -w 2
```

## Metadata

- `is_student`: Current student (boolean)

## Endpoints

- `/linked-role` - Start verification
- `/discord/callback` - Discord callback
- `/ucam/callback` - Cambridge callback
- `/preview/success` - Preview of success page
- `/preview/error` - Preview of error page
