# Discord Cambridge Linked Role

Verifies University of Cambridge members via Microsoft Entra ID with the University Central Directory for Discord applications.

## Setup

1. See https://discord.com/developers/applications
2. Setup https://toolkit.uis.cam.ac.uk
3. Copy `.env.example` to `.env` and fill in credentials
4. Install: `uv pip install .`
5. Register metadata with Discord: `uv run python -m src.register_metadata`
6. Run development: `uv run python -m src.app`
7. Run production: `uv run gunicorn wsgi:app -b "0.0.0.0:5000" -w 2`

## Metadata

-   `is_student`: Current student (boolean)

## Endpoints

-   `/linked-role` - Start verification
-   `/discord/callback` - Discord callback
-   `/ucam/callback` - Cambridge callback
