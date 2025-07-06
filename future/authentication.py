"""
Base authentication interface.
"""


class Authentication:
    auth_type: str = ""


class UserPass(Authentication):
    # Regular username & password authentication, check against SQL database, generating a JWT
    auth_type = "basic"


class Kerberos(Authentication):
    # Kerberos Single Sign-On authentication
    auth_type = "sso"


class SAML(Authentication):
    # SAML Single Sign-On authentication
    auth_type = "sso"


class AzureAD(Authentication):
    # Azure AD authentication
    auth_type = "basic"


class OAuth(Authentication):
    # OAuth authentication
    auth_type = "oauth"
