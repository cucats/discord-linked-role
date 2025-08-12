from msal import ConfidentialClientApplication, Prompt
from msgraph import GraphServiceClient
from azure.core.credentials import TokenCredential, AccessToken

from .config import UCAM_CLIENT_ID, UCAM_CLIENT_SECRET, UCAM_REDIRECT_URI


TENANT_ID = "49a50445-bdfa-4b79-ade3-547b4f3986e9"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read"]

app = ConfidentialClientApplication(
    client_id=UCAM_CLIENT_ID,
    client_credential=UCAM_CLIENT_SECRET,
    authority=AUTHORITY,
)


def get_authorization_url(state: str) -> str:
    return app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=UCAM_REDIRECT_URI,
        state=state,
        prompt=Prompt.SELECT_ACCOUNT,
        domain_hint="cam.ac.uk",
    )


def get_tokens(code: str) -> dict:
    tokens = app.acquire_token_by_authorization_code(
        code=code,
        scopes=SCOPES,
        redirect_uri=UCAM_REDIRECT_URI,
    )

    if "error" in tokens:
        raise RuntimeError(
            f"Token exchange failed: {tokens['error']}: {tokens['error_description']}"
        )

    return tokens


# https://help.uis.cam.ac.uk/service/accounts-passwords/it-staff/university-central-directory/understanding-users-and-groups


class EntraIdGroup:
    UOC_USERS_STAFF = "1f440b90-597d-45b4-9a0d-11707f784de7"
    UOC_USERS_STUDENT = "0cbcd7fb-1f17-48fc-ac3e-4a22131fa92d"
    UOC_USERS_ALUMNI = "bc7a045e-6775-423a-abc6-deac53b50712"
    UOC_USERS_CAM_UPN = "b7a0f932-5964-41b2-9bb0-9b8cadf6b999"
    UOC_USERS_GUESTS = "20c3c1f1-309f-497d-9169-3ac4907098a1"
    UOC_USERS_ALL = "cc2cdd8b-eace-4a4b-a950-9b989a183b97"


class Token(TokenCredential):
    def __init__(self, access_token: str):
        import time

        self.access_token = AccessToken(
            access_token, expires_on=int(time.time()) + 3600
        )

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        return self.access_token


class GraphClient(GraphServiceClient):
    async def user_principal_name(self) -> str | None:
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
        return EntraIdGroup.UOC_USERS_STUDENT in [group.id for group in member_of.value]
