import secrets

from flask import Flask, request, redirect, session, render_template

from src import discord, ucam
from .config import FLASK_SECRET

app = Flask(__name__)
app.secret_key = FLASK_SECRET


@app.route("/linked-role")
async def linked_role():
    authorization_url, state = discord.get_authorization_url()
    session["discord_state"] = state
    return redirect(authorization_url)


@app.route("/discord/callback")
async def discord_callback():
    try:
        assert request.args.get("state") == session.get("discord_state"), ""
        code = request.args.get("code")

        session["discord_tokens"] = discord.get_tokens(code)

        state = session["ucam_state"] = secrets.token_urlsafe(32)
        authorization_url = ucam.get_authorization_url(state)
        return redirect(authorization_url)

    except Exception as e:
        print(e)
        return (
            render_template(
                "error.j2",
                message="An error occurred during Discord authentication.",
            ),
            500,
        )


@app.route("/ucam/callback")
async def ucam_callback():
    try:
        assert request.args.get("state") == session.get("ucam_state")
        code = request.args.get("code")
        ucam_tokens = ucam.get_tokens(code)

        discord_tokens = session["discord_tokens"]
        if not discord_tokens:
            return

        credentials = ucam.Token(ucam_tokens["access_token"])
        client = ucam.GraphClient(credentials)

        upn = await client.user_principal_name()
        assert upn is not None

        is_student = await client.is_student()

        metadata = {
            "is_student": "1" if is_student else "0",
        }

        discord.push_metadata(discord_tokens, metadata)

        return render_template(
            "success.j2",
            crsid=upn,
            is_student=is_student,
        )

    except Exception as e:
        print(e)
        return (
            render_template(
                "error.j2",
                message="An error occurred during authentication.",
            ),
            500,
        )


@app.route("/preview/success")
def preview_success():
    return render_template(
        "success.j2",
        crsid="Preview",
        is_student=True,
    )


@app.route("/preview/error")
def preview_error():
    return render_template(
        "error.j2",
        message="Preview",
    )
