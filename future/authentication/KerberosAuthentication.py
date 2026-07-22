"""
Kerberos Single Sign-On authentication.
"""

from future.authentication.Authentication import BaseAuthentication


class KerberosAuthentication(BaseAuthentication):
    auth_type = "sso"
