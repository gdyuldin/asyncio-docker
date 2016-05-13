class APIError(Exception):
    pass


class StatusError(APIError):

    def __init__(self, *args, **kwargs):
        self.status = kwargs.pop('status', None)
        super(StatusError, self).__init__(*args, **kwargs)


class Status304Error(StatusError):
    pass


class Status400Error(StatusError):
    pass


class Status403Error(StatusError):
    pass


class Status404Error(StatusError):
    pass


class Status409Error(StatusError):
    pass


class Status500Error(StatusError):
    pass


class StatusUnknownError(StatusError):
    pass


_status_errors = {
    304: Status304Error,
    400: Status400Error,
    403: Status403Error,
    404: Status404Error,
    409: Status409Error,
    500: Status500Error
}

async def status_error(res):
    message = await res.text()
    if res.status in _status_errors:
        return _status_errors[res.status](message, status=res.status)
    else:
        return StatusUnknownError(message, status=res.status)
