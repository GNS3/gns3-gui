""" Exception classes for CloudCtrl classes. """


class ApiError(Exception):

    """ Raised when the server returns 500 Compute Error. """
    pass


class BadRequest(Exception):

    """ Raised when the server returns 400 Bad Request. """
    pass


class ComputeFault(Exception):

    """ Raised when the server returns 400|500 Compute Fault. """
    pass


class Forbidden(Exception):

    """ Raised when the server returns 403 Forbidden. """
    pass


class ItemNotFound(Exception):

    """ Raised when the server returns 404 Not Found. """
    pass


class KeyPairExists(Exception):

    """ Raised when the server returns 409 Conflict Key pair exists. """
    pass


class MethodNotAllowed(Exception):

    """ Raised when the server returns 405 Method Not Allowed. """
    pass


class OverLimit(Exception):

    """ Raised when the server returns 413 Over Limit. """
    pass


class ServerCapacityUnavailable(Exception):

    """ Raised when the server returns 503 Server Capacity Uavailable. """
    pass


class ServiceUnavailable(Exception):

    """ Raised when the server returns 503 Service Unavailable. """
    pass


class Unauthorized(Exception):

    """ Raised when the server returns 401 Unauthorized. """
    pass
