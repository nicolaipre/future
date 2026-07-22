"""
OAuth 2 authentication.
"""

from future.authentication.Authentication import Authentication


class OAuth2Authentication(Authentication):
    auth_type = "oauth"
