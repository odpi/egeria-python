<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

![Egeria Logo](https://egeria-project.org/assets/images/egeria-header.png)

[![GitHub](https://img.shields.io/github/license/odpi/egeria)](LICENSE)


# pyegeria: a python client for Egeria

This is a package for easily using the Egeria
open metadata environment from python. Details about the
open source Egeria project can be found at [Egeria Project](https://egeria-project.org).

This package is in active development. There is initial
support for many of Egeria's services including configuration and operation.  This client depends on 
This release supports Egeria 5.1 and above - although most of the functions may work on earlier versions of Egeria as well. 

The code is organized to mimic the existing Egeria Java Client structure.

WARNING: files that start with "X" are in-progress placeholders that are not meant to be used..they will mature and 
evolve.

All feedback is welcome. Please engage via our [community](http://egeria-project.org/guides/community/), 
team calls, or via github issues in this repo. If interested in contributing,
you can engage via the community or directly reach out to
[dan.wolfson\@pdr-associates.com](mailto:dan.wolfson@pdr-associates.com?subject=pyegeria).

This is a learning experience.



----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the ODPi Egeria project.

## Exceptions in pyegeria

pyegeria standardizes error handling around a clear hierarchy of exceptions defined in `_exceptions_new.py`. All high‑level exceptions inherit from the common base `PyegeriaException`, so you can safely catch `PyegeriaException` to handle any error raised by this library. For more granular handling, use the specific subclasses listed below.

Key classes:
- `PyegeriaException` (base)
  - Common base for all pyegeria exceptions. Contains:
    - `response`: the HTTP response (if any) from the Egeria server
    - `response_url`: the URL called (if available)
    - `response_code`: HTTP status code (if available)
    - `response_egeria_msg_id`/`response_egeria_msg`: fields extracted from Egeria error bodies (if present)
    - `error_code`: a `PyegeriaErrorCode` value providing a message template, system_action, and user_action
    - `context`/`additional_info`: extra details provided by the caller
  - Catch this when you want a single handler for all pyegeria exceptions.

- `PyegeriaInvalidParameterException`
  - Raised when client parameters are invalid or missing.

- `PyegeriaAPIException`
  - Raised when Egeria reports a server‑side error (non‑200 response). The original HTTP response is preserved, and the exception extracts Egeria’s `relatedHTTPCode` and error details for you.

- `PyegeriaUnauthorizedException`
  - Raised when the server indicates the caller is not authorized for the requested action.

- `PyegeriaNotFoundException`
  - Raised when a requested resource cannot be found.

- `PyegeriaConnectionException`
  - Raised when client‑side connectivity fails (e.g., network/timeout issues) before a valid Egeria response is received.

- `PyegeriaClientException`
  - Raised for other client‑side errors that do not fall into validation or connectivity categories but are not server errors.

- `PyegeriaUnknownException`
  - Raised when an unexpected condition occurs that does not map cleanly to another exception class.

Printing exceptions
- Use `print_basic_exception(e)` for a concise, formatted summary. It includes the underlying exception class name (for example, `PyegeriaAPIException`) and key details such as HTTP code, reason, request URL, and Egeria message/user action when available.
- Use `print_exception_table(e)` for a more verbose, tabular view of the full Egeria error payload.
- For Pydantic validation failures, catch `pydantic_core.ValidationError` and use `print_validation_error(e)` to render the error details clearly.

Examples

```python
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaInvalidParameterException,
    print_basic_exception,
    print_validation_error,
)

try:
    # call a pyegeria client method that reaches an Egeria server
    client.set_event_bus("EventBusConfig", "egeria.omag")
except PyegeriaInvalidParameterException as e:
    print_basic_exception(e)  # specific handling for bad inputs
except PyegeriaAPIException as e:
    print_basic_exception(e)  # server‑side issue, response preserved
except PyegeriaException as e:
    print_basic_exception(e)  # generic catch for any pyegeria error
```

Generic catch validity
- All pyegeria exceptions inherit from `PyegeriaException`, so it is suitable for use as a single generic catch that will capture any other pyegeria exception.
- The printing helpers (`print_basic_exception`, `print_exception_table`) include the name of the actual underlying exception class in their output title, so you can still differentiate the type even when catching the base class.