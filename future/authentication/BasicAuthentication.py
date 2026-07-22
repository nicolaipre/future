"""
Regular username & password authentication (check against SQL database, generating a JWT).
"""

from future.authentication.Authentication import Authentication


class BasicAuthentication(Authentication):
    auth_type = "basic"
