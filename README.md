# Discord Cambridge Linked Role

Verifies University of Cambridge members via Open ID Connect (OIDC) with the University Central Directory (UDC) for Discord applications.

## Setup

1. Follow https://discord.com/developers/applications
2. Setup https://toolkit.uis.cam.ac.uk
3. Copy `.env.example` to `.env` and fill in credentials
4. Install: `uv pip install .`
5. Initialise database: `uv run python -m src.database`
6. Register metadata with Discord: `uv run python -m src.register_metadata`
7. Run development: `uv run python -m src.app`
8. Run production: `uv run gunicorn wsgi:app -b "0.0.0.0:8000" -w 2`

## Metadata

-   `is_student`: Current student (boolean)

## Endpoints

-   `/linked-role` - Start verification
-   `/discord-oauth-callback` - Discord callback
-   `/ucd-oidc-callback` - UCD callback
