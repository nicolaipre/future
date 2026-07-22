"""
Keycloak authentication.
"""

from future.authentication.Authentication import Authentication


class KeycloakAuthentication(Authentication):
    auth_type = "oauth"
