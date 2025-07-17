from flask import Flask, request, redirect, session, render_template_string
from datetime import datetime
from src import config, discord_oauth, oidc, database

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


@app.route("/")
def index():
    return "Running"


@app.route("/linked-role")
async def linked_role():
    oauth_data = discord_oauth.get_oauth_url()
    session["discord_state"] = oauth_data["state"]
    return redirect(oauth_data["url"])


@app.route("/discord-oauth-callback")
async def discord_oauth_callback():
    """Discord OAuth callback"""
    try:
        # Verify state
        state = request.args.get("state")
        if state != session.get("discord_state"):
            return "State verification failed", 403

        # Get tokens
        code = request.args.get("code")
        tokens = discord_oauth.get_oauth_tokens(code)

        # Get user data
        user_data = discord_oauth.get_user_data(tokens)
        user_id = user_data["user"]["id"]

        # Store tokens
        tokens["expires_at"] = datetime.now().timestamp() + tokens["expires_in"]
        await database.store_discord_tokens(user_id, tokens)

        # Always redirect to UCD OIDC for fresh verification
        oidc_data = oidc.get_oidc_auth_url(user_id)
        session["oidc_state"] = oidc_data["state"]
        return redirect(oidc_data["url"])

    except Exception as e:
        print(f"Discord OAuth Error: {e}")
        return (
            render_template_string(
                ERROR_TEMPLATE,
                message="An error occurred during Discord authentication.",
                retry_url=None,
            ),
            500,
        )


@app.route("/ucd-oidc-callback")
async def ucd_oidc_callback():
    """UCD OIDC callback"""
    try:
        # Verify state and extract Discord user ID
        state = request.args.get("state")
        stored_state = session.get("oidc_state")

        if (
            not state
            or not stored_state
            or not state.startswith(stored_state.split(":")[0])
        ):
            return (
                render_template_string(
                    ERROR_TEMPLATE, message="Invalid state parameter.", retry_url=None
                ),
                403,
            )

        discord_user_id = state.split(":")[0]

        # Get OIDC tokens
        code = request.args.get("code")
        tokens = oidc.get_oidc_tokens(code)

        # Get user info
        user_info = oidc.get_user_info(tokens["access_token"])

        # Verify Cambridge user
        verification = oidc.verify_cambridge_user(user_info)

        if not verification["verified"]:
            return (
                render_template_string(
                    ERROR_TEMPLATE,
                    message="You must sign in with a valid @cam.ac.uk account.",
                    retry_url=f"/retry?user_id={discord_user_id}",
                ),
                400,
            )

        # Store verification with UPN
        await database.store_verification(
            discord_user_id, verification["upn"], verification["is_student"]
        )

        # Update Discord metadata
        await update_metadata(discord_user_id, verification)

        # Show verification info in success page
        return render_template_string(
            SUCCESS_TEMPLATE,
            crsid=verification["upn"],
            is_student=verification.get("is_student", False),
        )

    except Exception as e:
        print(f"UCD OIDC error: {e}")
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
    """Retry verification for a user."""
    user_id = request.args.get("user_id")
    if not user_id:
        return redirect("/")

    # Redirect straight to UCD OIDC
    oidc_data = oidc.get_oidc_auth_url(user_id)
    session["oidc_state"] = oidc_data["state"]
    return redirect(oidc_data["url"])


async def update_metadata(user_id: str, verification: dict):
    """Update Discord metadata for a user."""
    tokens = await database.get_discord_tokens(user_id)
    if not tokens:
        return

    if verification and verification.get("verified"):
        metadata = {
            "is_student": "1" if verification.get("is_student", False) else "0",
        }
    else:
        metadata = {
            "is_student": "0",
        }

    await discord_oauth.push_metadata(user_id, tokens, metadata)
