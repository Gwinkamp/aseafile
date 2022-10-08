# aseafile

Asynchronous [seafile](https://www.seafile.com/en/home/)

Unofficial library that provides the API methods of the seafile service

## Installation

```commandline
pip install aseafile --upgrade
```

## Features

This library is asynchronous

At the moment, the library has support several sections of
the [seafile web api](https://download.seafile.com/published/web-api/home.md):

* [directories management](https://download.seafile.com/published/web-api/v2.1/directories.md)
* [files managment](https://download.seafile.com/published/web-api/v2.1/file.md)
* [upload file](https://download.seafile.com/published/web-api/v2.1/file-upload.md)
* [libraries (repositories) managment](https://download.seafile.com/published/web-api/v2.1/libraries.md)

> Currently, only version 2.1 of the seafile web api is supported

## Dependencies

> python version **3.10** minimum required

Requirements python libraries:

* [aiohttp](https://docs.aiohttp.org/en/stable/)
* [pydantic](https://github.com/pydantic/pydantic)

## Getting started

Creating an instance of http client and verifying that the service is running using the "ping" method:

```python
import asyncio
from aseafile import SeafileHttpClient


async def main():
    client = SeafileHttpClient(base_url='http://seafile.example.com')

    result = await client.ping()
    print(result.content)  # pong


if __name__ == '__main__':
    asyncio.run(main())
```

Obtaining access token and sending "auth ping":

```python
import asyncio
from aseafile import SeafileHttpClient


async def main():
    client = SeafileHttpClient(base_url='http://seafile.example.com')

    token_result = await client.obtain_auth_token(username='my@example.com', password='Test123456')

    result = await client.auth_ping(token=token_result.content)
    print(result.content)  # pong


if __name__ == '__main__':
    asyncio.run(main())
```

Authorization in the service with automatic token saving and sending "auth ping":

```python
import asyncio
from aseafile import SeafileHttpClient


async def main():
    client = SeafileHttpClient(base_url='http://seafile.example.com')

    await client.authorize(username='my@example.com', password='Test123456')

    result = await client.auth_ping()
    print(result.content)  # pong


if __name__ == '__main__':
    asyncio.run(main())
```

## Contributing

free

