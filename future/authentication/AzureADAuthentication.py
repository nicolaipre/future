"""
Azure AD authentication.
"""

from future.authentication.Authentication import BaseAuthentication


class AzureADAuthentication(BaseAuthentication):
    auth_type = "basic"
