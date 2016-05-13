class ClientError(Exception):
    pass


class ClientClosedError(ClientError):
    pass
