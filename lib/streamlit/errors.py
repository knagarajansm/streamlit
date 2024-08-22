# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2024)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import gettext
from typing import Any

from streamlit import util


class Error(Exception):
    """The base class for all exceptions thrown by Streamlit.

    Should be used for exceptions raised due to user errors (typically via
    StreamlitAPIException) as well as exceptions raised by Streamlit's internal
    code.
    """

    pass


class CustomComponentError(Error):
    """Exceptions thrown in the custom components code path."""

    pass


class DeprecationError(Error):
    pass


class FragmentStorageKeyError(Error, KeyError):
    """A KeyError raised when a KeyError is encountered during a FragmentStorage
    operation."""

    pass


class FragmentHandledException(Exception):
    """An exception that is raised by the fragment
    when it has handled the exception itself.
    """

    pass


class NoStaticFiles(Error):
    pass


class NoSessionContext(Error):
    pass


class MarkdownFormattedException(Error):
    """Exceptions with Markdown in their description.

    Instances of this class can use markdown in their messages, which will get
    nicely formatted on the frontend.
    """

    pass


class UncaughtAppException(Error):
    """Catchall exception type for uncaught exceptions that occur during script execution."""

    def __init__(self, exc):
        self.exc = exc


class StreamlitAPIException(MarkdownFormattedException):
    """Base class for Streamlit API exceptions.

    An API exception should be thrown when user code interacts with the
    Streamlit API incorrectly. (That is, when we throw an exception as a
    result of a user's malformed `st.foo` call, it should be a
    StreamlitAPIException or subclass.)

    When displaying these exceptions on the frontend, we strip Streamlit
    entries from the stack trace so that the user doesn't see a bunch of
    noise related to Streamlit internals.

    """

    def __repr__(self) -> str:
        return util.repr_(self)


class DuplicateWidgetID(StreamlitAPIException):
    pass


class UnserializableSessionStateError(StreamlitAPIException):
    pass


class StreamlitAPIWarning(StreamlitAPIException, Warning):
    """Used to display a warning.

    Note that this should not be "raised", but passed to st.exception
    instead.
    """

    def __init__(self, *args):
        super().__init__(*args)
        import inspect
        import traceback

        f = inspect.currentframe()
        self.tacked_on_stack = traceback.extract_stack(f)

    def __repr__(self) -> str:
        return util.repr_(self)


class StreamlitModuleNotFoundError(StreamlitAPIWarning):
    """Print a pretty message when a Streamlit command requires a dependency
    that is not one of our core dependencies."""

    def __init__(self, module_name, *args):
        message = (
            f'This Streamlit command requires module "{module_name}" to be '
            "installed."
        )
        super().__init__(message, *args)


class LocalizableStreamlitException(StreamlitAPIException):
    def __init__(self, message: str, **kwargs):
        exception_name = type(self).__name__
        exception_message = gettext.gettext(exception_name)
        if exception_message == exception_name:
            # gettext returns the message ID if there is no translation.
            # In this case, we want to use the message provided in the constructor.
            exception_message = message
        super().__init__((exception_message).format(**kwargs))
        self._exec_kwargs = kwargs

    @property
    def exec_kwargs(self) -> dict[str, Any]:
        return self._exec_kwargs


class StreamlitNumberInputDifferentTypesError(LocalizableStreamlitException):
    """Exception raised mixing floats and ints in st.number_input."""

    def __init__(
        self,
        value: int | float,
        min_value: int | float,
        max_value: int | float,
        step: int | float,
    ):
        error_message = "All numerical arguments must be of the same type."

        if value:
            value_type = type(value).__name__
            error_message += f"\n`value` has {value_type} type."

        if min_value:
            min_value_type = type(min_value).__name__
            error_message += f"\n`min_value` has {min_value_type} type."

        if max_value:
            max_value_type = type(max_value).__name__
            error_message += f"\n`max_value` has {max_value_type} type."

        if step:
            step_type = type(step).__name__
            error_message += f"\n`step` has {step_type} type."

        super().__init__(error_message)


class StreamlitInputInvalidValueError(LocalizableStreamlitException):
    """Exception raised when the `min_value` is greater or the `max_value` is less than the `value` in `st.number_input`."""

    def __init__(
        self, value: int | float, min_value: int | float, max_value: int | float
    ):
        error_message = None

        if value < min_value:
            error_message = (
                f"The `value` {value} is less than the `min_value` {min_value}."
            )
        elif value > max_value:
            error_message = (
                f"The `value` {value} is greater than the `max_value` {max_value}."
            )

        super().__init__(error_message)


class StreamlitJSNumberBoundsError(LocalizableStreamlitException):
    """Exception raised when a number exceeds the Javascript limits."""

    def __init__(self, message: str):
        super().__init__(message)


class StreamlitNumberInputInvalidFormatError(LocalizableStreamlitException):
    """Exception raised when the format string for `st.number_input` contains
    invalid characters.
    """

    def __init__(self, format: str):
        super().__init__(
            f"Format string for st.number_input contains invalid characters: {format}"
        )
