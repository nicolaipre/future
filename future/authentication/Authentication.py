"""
Base authentication interface.
"""


class Authentication:
    auth_type: str = ""


# Alias for stubs that subclass BaseAuthentication (Azure AD, Kerberos, …).
BaseAuthentication = Authentication
