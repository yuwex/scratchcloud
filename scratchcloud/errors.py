class ScratchCloudException(Exception):
    """Base ScratchCloud exception.
    Use this to catch all exceptions raised by this library.
    """

    pass

class SizeError(ScratchCloudException):
    """Size Error.
    Raised when a cloud variable payload is too large.
    """
    
    pass


class NotFoundError(ScratchCloudException):
    """Not Found Error.
    Raised when data from the API is not found.
    """
    
    pass

class EncodeError(ScratchCloudException):
    """Encode Error.
    Raised when there is an issue with encoding.
    """
    
    pass

class DecodeError(ScratchCloudException):
    """Decode Error.
    Raised when there is an issue with decoding.
    """
    
    pass

class MissingCloudVariable(ScratchCloudException):
    """Missing Cloud Variable.
    Raised when specified cloud variables are missing, or when a project doesn't have cloud variables.
    """

    pass

class UnableToValidate(ScratchCloudException):
    """UnableToValidate.
    Raised when an issue occurs with username validation.
    """

    pass