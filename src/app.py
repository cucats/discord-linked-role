from flask import Flask, request, redirect, session, render_template_string
from datetime import datetime
from src import config, discord, ucam

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET


SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Verification Successful</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .container { background: #e8f5e9; padding: 30px; border-radius: 10px; }
        h1 { color: #2e7d32; text-align: center; }
        .details { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .detail-row { margin: 10px 0; display: flex; justify-content: space-between; }
        .label { font-weight: bold; color: #555; }
        .value { color: #333; }
        .info { color: #666; margin-top: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Verification Successful!</h1>
        <div class="details">
            <div class="detail-row">
                <span class="label">Account:</span>
                <span class="value">{{ crsid }}</span>
            </div>
            <div class="detail-row">
                <span class="label">Status:</span>
                <span class="value">{{ "Current Student" if is_student else "Cambridge Member" }}</span>
            </div>
        </div>
        <p class="info">You can now close this window and return to Discord.<br>Your linked role will be updated automatically.</p>
    </div>
</body>
</html>
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Verification Failed</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
        .container { background: #ffebee; padding: 30px; border-radius: 10px; text-align: center; }
        h1 { color: #c62828; }
        .button { 
            background: #5865F2; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 5px; 
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Verification Failed</h1>
        <p>{{ message }}</p>
        {% if retry_url %}
        <a href="{{ retry_url }}" class="button">Try Again</a>
        {% endif %}
    </div>
</body>
</html>
"""


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
        tokens = discord.get_token(code)
        user_data = discord.get_user_data(tokens)
        user_id = user_data["user"]["id"]
        tokens["expires_at"] = datetime.now().timestamp() + tokens["expires_in"]
        session[f"discord_tokens_{user_id}"] = tokens
        authorization_url, state = ucam.get_auth_url(user_id)
        session["ucam_state"] = state
        return redirect(authorization_url)

    except Exception as e:
        print(e)
        return (
            render_template_string(
                ERROR_TEMPLATE,
                message="An error occurred during Discord authentication.",
                retry_url=None,
            ),
            500,
        )


@app.route("/ucam/callback")
async def ucd_ucam_callback():
    try:
        assert request.args.get("state") == session.get("ucam_state")
        discord_user_id = state.split(":")[0]
        code = request.args.get("code")
        tokens = ucam.get_token(code)
        user_info = ucam.get_user_info(tokens["access_token"])
        is_student = ucam.is_student(user_info)
        upn = user_info.get("userPrincipalName", "")
        verification = {"verified": True, "upn": upn, "is_student": is_student}

        await update_metadata(discord_user_id, verification)

        return render_template_string(
            SUCCESS_TEMPLATE,
            crsid=upn,
            is_student=is_student,
        )

    except Exception as e:
        print(e)
        return (
            render_template_string(
                ERROR_TEMPLATE,
                message="An error occurred during authentication.",
                retry_url=None,
            ),
            500,
        )


@app.route("/retry")
async def retry_verification():
    user_id = request.args.get("user_id")
    if not user_id:
        return redirect("/")

    authorization_url, state = ucam.get_auth_url(user_id)
    session["ucam_state"] = state
    return redirect(authorization_url)


async def update_metadata(user_id: str, verification: dict):
    tokens = session.get(f"discord_tokens_{user_id}")
    if not tokens:
        return

    if verification.get("verified"):
        metadata = {
            "is_student": "1" if verification.get("is_student", False) else "0",
        }
    else:
        metadata = {
            "is_student": "0",
        }

    await discord.push_metadata(tokens, metadata)
