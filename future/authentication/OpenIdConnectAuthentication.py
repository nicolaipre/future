"""
OpenID Connect authentication.
"""

from future.authentication.Authentication import Authentication


class OpenIdConnectAuthentication(Authentication):
    auth_type = "oidc"
