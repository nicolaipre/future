"""
Auth0 authentication.
"""

from future.authentication.Authentication import Authentication


class Auth0Authentication(Authentication):
    auth_type = "oauth"
