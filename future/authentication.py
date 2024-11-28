class Authentication:
    auth_type = None


class UserPass(Authentication):
    # Regular username & password authentication, check against SQL database, generating a JWT
    auth_type = "userpass"


class SSO(Authentication):
    # SSO / SAML authentication
    auth_type = "sso"
