from strenum import StrEnum


class HttpMethod(StrEnum):

    def __new__(cls, value: str, description: str | None = None):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    UNKNOWN = (
        'unknown',
        'Unknown http method. Please read http documentation https://www.w3.org/Protocols/rfc2068/rfc2068')

    GET = (
        'get',
        'GET method is used to retrieve information from the given server using a given URI.'
    )

    POST = (
        'post',
        'POST request method requests that a web server accepts the data enclosed in the body of the request message, '
        'most likely for storing it'
    )

    PUT = (
        'put',
        'The PUT method requests that the enclosed entity be stored under the supplied URI. '
        'If the URI refers to an already existing resource, it is modified and if the URI does not point to an '
        'existing resource, then the server can create the resource with that URI.'
    )

    DELETE = (
        'delete',
        'The DELETE method deletes the specified resource'
    )

    HEAD = (
        'head',
        'The HEAD method asks for a response identical to that of a GET request, but without the response body.'
    )

    PATCH = (
        'patch',
        '	It is used for modify capabilities. The PATCH request only needs to contain the changes to the resource, '
        'not the complete resource'
    )
