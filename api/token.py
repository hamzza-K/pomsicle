class Token:
    """
    Class for managing authentication tokens.
    """
    def __init__(self, access_token, expires_in):
        self.access_token = access_token
        self.expires_in = expires_in

