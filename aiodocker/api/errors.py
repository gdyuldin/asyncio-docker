class APIError(Exception):
    pass


class Status304Error(APIError):
    pass


class Status404Error(APIError):
    pass


class Status500Error(APIError):
    pass


class StatusUnknownError(APIError):
    pass


_status_errors = {
    304: Status304Error,
    404: Status404Error,
    500: Status500Error
}

def status_error(status):
    if status in _status_errors:
        return _status_errors[status]
    else:
        return StatusUnknownError(status)
