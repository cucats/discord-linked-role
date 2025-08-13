<div align="center">

# Discord Linked Role for the University of Cambridge

[![CI](https://github.com/cucats/discord-linked-role/actions/workflows/ci.yml/badge.svg)](https://github.com/cucats/discord-linked-role/actions/workflows/ci.yml)
[![CD](https://github.com/cucats/discord-linked-role/actions/workflows/cd.yml/badge.svg)](https://github.com/cucats/discord-linked-role/actions/workflows/cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://ghcr.io/cucats/discord-linked-role)

Verifies University of Cambridge students via Microsoft Entra ID for a Discord linked role.

</div>

## Prerequisites

Obtain a Client ID, Client Secret, and Bot token from https://discord.com/developers/applications
Obtain a Client ID and Client Secret from https://toolkit.uis.cam.ac.uk/endpoints

## Setup

Make sure these environment variables are set.

```conf
HOST=
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
