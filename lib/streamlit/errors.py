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
import os
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


# st.number_input
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


class StreamlitNumberInputInvalidMinValueError(LocalizableStreamlitException):
    """Exception raised when the `min_value` is greater than the `value` in `st.number_input`."""

    def __init__(self, value: int | float, max_value: int | float):
        super().__init__(
            "The `value` {value} is greater than the `max_value` {max_value}.",
            value=value,
            max_value=max_value,
        )


class StreamlitNumberInputInvalidMaxValueError(LocalizableStreamlitException):
    """Exception raised when the `max_value` is less than the `value` in `st.number_input`."""

    def __init__(
        self, value: int | float, min_value: int | float, max_value: int | float
    ):
        super().__init__(
            "The `value` {value} is less than the `min_value` {min_value}.",
            value=value,
            min_value=min_value,
        )


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


# st.page_link
class StreamlitMissingPageLabelError(LocalizableStreamlitException):
    """Exception raised when a page_link is created without a label."""

    def __init__(self):
        super().__init__(
            "The `label` param is required for external links used with `st.page_link` - please provide a `label`."
        )


class StreamlitPageNotFoundError(LocalizableStreamlitException):
    """Exception raised the linked page can not be found."""

    def __init__(self, page: str, main_script_directory: str):
        super().__init__(
            f"Could not find page: `{page}`. You must provide a file path "
            f"relative to the entrypoint file (from the directory `{os.path.basename(main_script_directory)}`). "
            "Only the entrypoint file and files in the `pages/` directory are supported."
        )


class StreamlitPageNotFoundMPAV2Error(LocalizableStreamlitException):
    """Exception raised the linked page can not be found."""

    def __init__(self, page: str):
        super().__init__(
            f"Could not find page: `{page}`. You must provide a `StreamlitPage` "
            "object or file path relative to the entrypoint file. Only pages "
            "previously defined by [st.Page](http://st.page/) and passed to "
            "`st.navigation` are allowed."
        )


# policies
class StreamlitFragmentWidgetsNotAllowedOutsideError(LocalizableStreamlitException):
    """Exception raised when the fragment attempts to write to an element outside of its container."""

    def __init__(self):
        super().__init__(" Fragments cannot write widgets to outside containers.")


class StreamlitInvalidFormCallbackError(LocalizableStreamlitException):
    """Exception raised a `on_change` callback is set on any element in a form except for the `st.form_submit_button`."""

    def __init__(self):
        super().__init__(
            "Within a form, callbacks can only be defined on st.form_submit_button. "
            "Defining callbacks on other widgets inside a form is not allowed."
        )


class StreamlitWidgetValueAssignmentNotAllowedError(LocalizableStreamlitException):
    """Exception raised when trying to set values for a widget where writes are not allowed."""

    def __init__(self, key: str):
        super().__init__(
            f"Values for the widget with `key` '{key}' cannot be set using `st.session_state`."
        )


# st.multiselect
class StreamlitSelectionCountExceedsMaxError(LocalizableStreamlitException):
    """Exception raised when there are more default selections specified than the max allowable selections."""

    def __init__(self, current_selections_count: int, max_selections_count: int):
        curr_selections_noun = (
            "selection" if current_selections_count == 1 else "selections"
        )
        options_noun = "option" if max_selections_count == 1 else "options"

        super().__init__(
            f"Multiselect has {current_selections_count} {curr_selections_noun} "
            f"selected but `max_selections` is set to {max_selections_count}. "
            "This happened because you either gave too many options to `default` "
            "or you manipulated the widget's state through `st.session_state`. "
            "Note that the latter can happen before the line indicated in the traceback. "
            f"Please select at most {max_selections_count} {options_noun}."
        )


# st.columns
class StreamlitInvalidColumnSpecError(LocalizableStreamlitException):
    """Exception raised when no weights are specified, or a negative weight is specified."""

    def __init__(self):
        super().__init__(
            "The spec argument to `st.columns` must be either a "
            "positive integer (number of columns) or a list of positive numbers (width ratios of the columns). "
            "See [documentation](https://docs.streamlit.io/develop/api-reference/layout/st.columns) "
            "for more information."
        )


# st.set_page_config
class StreamlitSetPageConfigMustBeFirstCommandError(LocalizableStreamlitException):
    """Exception raised when the set_page_config command is not the first executed streamlit command."""

    def __init__(self):
        super().__init__(
            "`set_page_config()` can only be called once per app page, "
            "and must be called as the first Streamlit command in your script.\n\n"
            "For more information refer to the [docs]"
            "(https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config)."
        )


class StreamlitInvalidLayoutError(LocalizableStreamlitException):
    """Exception raised when an invalid value is specified for layout."""

    def __init__(self, layout: str):
        super().__init__(f'layout must be "centered" or "wide" (got "{layout}")')


class StreamlitInvalidSidebarStateError(LocalizableStreamlitException):
    """Exception raised when an invalid value is specified for `initial_sidebar_state`."""

    def __init__(self, initial_sidebar_state: str):
        super().__init__(
            f'initial_sidebar_state must be "auto" or "expanded" or "collapsed" (got "{initial_sidebar_state}")'
        )


class StreamlitInvalidMenuItemKeyError(LocalizableStreamlitException):
    """Exception raised when an invalid key is specified."""

    def __init__(self, key: str):
        super().__init__(
            f'We only accept the keys: "Get help", "Report a bug", and "About" ("{key}" is not a valid key.)'
        )


class StreamlitInvalidURLError(LocalizableStreamlitException):
    """Exception raised when an invalid URL is specified for any of the menu items except for “About”."""

    def __init__(self, url: str):
        super().__init__(
            f'"{url}" is a not a valid URL. '
            "You must use a fully qualified domain beginning with `http://`, `https://`, or `mailto:`."
        )
