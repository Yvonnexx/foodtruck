# -*- encoding: utf-8 -*-

"""All errors are defined here.

1000 level: internal api error
2000 level: external api error
3000 level: internal library error
4000 level: external library error
"""


def compose_message(error, **kwargs):
    return dict(
        error_code=error[0],
        error_message=error[1].format(**kwargs)
    )


class Error(Exception):
    def __str__(self):
        return repr(self.message)


class InvalidValueError(Error):
    def __init__(self, var, value):
        self.message = compose_message(
            invalid_value_error,
            var=var,
            value=value,
        )


class InternalAPIError(Error):
    def __init__(self, reason):
        self.message = compose_message(
            internal_api_error,
            reason=reason
        )


class HttpRequestFailedError(Error):
    def __init__(self, url, status_code):
        self.message = compose_message(
            http_request_failed_error,
            url=url,
            status_code=status_code,
        )


class HttpRequestError(Error):
    def __init__(self, url, reason):
        self.message = compose_message(
            http_request_error,
            url=url,
            reason=reason,
        )


class BuildKDTreeError(Error):
    def __init__(self, reason):
        self.message = compose_message(
            build_kdtree_error,
            reason=reason,
        )


invalid_value_error = (
    1001,
    'Invalid value for {var}: {value}',
)


internal_api_error = (
    1002,
    'Internal api error due to {reason}',
)


http_request_failed_error = (
    4001,
    'HTTP request to {url} failed, status code {status_code}',
)


http_request_error = (
    4002,
    'Error on HTTP request to {url} due to {reason}',
)


build_kdtree_error = (
    4011,
    'Error occured when builing kd-tree due to {reason}',
)
