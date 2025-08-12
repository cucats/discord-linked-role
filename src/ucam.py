from msal import ConfidentialClientApplication, Prompt
from msgraph import GraphServiceClient
from azure.core.credentials import TokenCredential, AccessToken
from src import config


TENANT_ID = "49a50445-bdfa-4b79-ade3-547b4f3986e9"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read"]

app = ConfidentialClientApplication(
    client_id=config.OIDC_CLIENT_ID,
    client_credential=config.OIDC_CLIENT_SECRET,
    authority=AUTHORITY,
)

# https://help.uis.cam.ac.uk/service/accounts-passwords/it-staff/university-central-directory/understanding-users-and-groups
UOC_USERS_STUDENT = "0cbcd7fb-1f17-48fc-ac3e-4a22131fa92d"


def get_authorization_url(state: str) -> str:
    return app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=config.OIDC_REDIRECT_URI,
        state=state,
        prompt=Prompt.SELECT_ACCOUNT,
        domain_hint="cam.ac.uk",
    )


def get_token(code: str) -> dict:
    result = app.acquire_token_by_authorization_code(
        code=code, scopes=SCOPES, redirect_uri=config.OIDC_REDIRECT_URI
    )

    if "error" in result:
        raise RuntimeError(
            f"Token exchange failed: {result['error']}: {result['error_description']}"
        )

    print(result)

    return result


class Token(TokenCredential):
    def __init__(self, access_token: str):
        import time

        self.access_token = AccessToken(
            access_token, expires_on=int(time.time()) + 3600
        )

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        return self.access_token


class GraphClient(GraphServiceClient):
    async def upn(self) -> str | None:
        user = await self.me.get()

        if not user:
            return None
        return user.user_principal_name

    async def is_student(self) -> bool:
        member_of = await self.me.member_of.get()

        if not member_of:
            return False
        if not member_of.value:
            return False
        return UOC_USERS_STUDENT in [group.id for group in member_of.value]
