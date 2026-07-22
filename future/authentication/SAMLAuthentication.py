"""
SAML Single Sign-On authentication.
"""

from future.authentication.Authentication import Authentication


class SAMLAuthentication(Authentication):
    auth_type = "sso"
