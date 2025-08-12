from flask import Flask, request, redirect, session, render_template
from datetime import datetime
from src import config, discord, ucam
import secrets

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET


@app.route("/")
def root():
    return "Running"


@app.route("/linked-role")
async def linked_role():
    authorization_url, state = discord.get_oauth_url()
    session["discord_state"] = state
    return redirect(authorization_url)


@app.route("/discord/callback")
async def discord_callback():
    try:
        assert request.args.get("state") == session.get("discord_state")
        code = request.args.get("code")

        tokens = session[f"discord_tokens"] = discord.get_token(code)

        state = session["ucam_state"] = secrets.token_urlsafe(32)
        authorization_url = ucam.get_authorization_url(state)
        return redirect(authorization_url)

    except Exception as e:
        print(e)
        return (
            render_template(
                "error.html",
                message="An error occurred during Discord authentication.",
                retry_url=None,
            ),
            500,
        )


@app.route("/ucam/callback")
async def ucd_ucam_callback():
    try:
        assert request.args.get("state") == session.get("ucam_state")
        code = request.args.get("code")

        tokens = ucam.get_token(code)
        credentials = ucam.Token(tokens["access_token"])
        client = ucam.GraphClient(credentials)

        upn = await client.upn()
        if upn is None:
            raise ValueError("No upn")
        is_student = await client.is_student()
        verification = {"upn": upn, "is_student": is_student}

        await update_metadata(verification)

        return render_template(
            "success.html",
            crsid=upn,
            is_student=is_student,
        )

    except Exception as e:
        print(e)
        return (
            render_template(
                "error.html",
                message="An error occurred during authentication.",
                retry_url=None,
            ),
            500,
        )


async def update_metadata(verification: dict):
    tokens = session.get(f"discord_tokens")

    if not tokens:
        return

    metadata = {
        "is_student": "1" if verification.get("is_student", False) else "0",
    }

    await discord.push_metadata(tokens, metadata)
