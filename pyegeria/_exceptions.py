"""
This module has been removed.

The project now uses only the new exceptions from `pyegeria._exceptions_new`.

Please update your imports, for example:

    from pyegeria._exceptions_new import (
        PyegeriaInvalidParameterException as InvalidParameterException,
        PyegeriaAPIException as PropertyServerException,
        PyegeriaUnauthorizedException as UserNotAuthorizedException,
        print_basic_exception as print_exception_response,
    )

"""

raise ImportError(
    "pyegeria._exceptions has been removed. Import from pyegeria._exceptions_new instead."
)
