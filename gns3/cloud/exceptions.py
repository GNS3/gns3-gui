""" Exception classes for CloudCtrl classes. """


class Unauthorized(Exception):

    """ Raised when the server returns 401 Unauthorized. """

    pass


class Forbidden(Exception):

    """ Raised when the server returns 403 Forbidden. """

    pass


class ItemNotFound(Exception):

    """ Raised when the server returns 404 Not Found. """

    pass


class OverLimit(Exception):

    """ Raised when the server returns 413 Over Limit. """

    pass


class ServiceUnavailable(Exception):

    """ Raised when the server returns 503 Service Unavailable. """

    pass


class ServerCapacityUnavailable(Exception):

    """ Raised when the server returns 503 Server Capacity Uavailable. """

    pass


class ComputeFault(Exception):

    """ Raised when the server returns 400|500 Compute Fault. """

    pass


class KeyPairExists(Exception):

    """ Raised when the server returns 409 Conflict Key pair exists. """

    pass
