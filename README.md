# Discord Cambridge Linked Role

Verifies University of Cambridge members via Open ID Connect (OIDC) with the University Central Directory (UDC) for Discord applications.

## Setup

1. Create Discord app at https://discord.com/developers/applications
2. Setup https://toolkit.uis.cam.ac.uk
3. Copy `.env.example` to `.env` and fill in credentials
4. Install: `uv pip install .`
5. Register metadata: `python -m src.register_metadata`
6. Run: `python -m src.app`

## Metadata Field

-   `is_student`: Current student (boolean)

## Endpoints

-   `/linked-role` - Start verification
-   `/discord-oauth-callback` - Discord callback
-   `/ucd-oidc-callback` - UCD callback

## Deployment with Gunicorn

1. Install dependencies: `uv pip install .`
2. Configure `.env` with production values
3. Run with Gunicorn:

```bash
exec gunicorn wsgi:app \
    --bind "unix:/path/to/socket.unix" \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
```
