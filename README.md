[![Tests](https://github.com/chrdio/api-funkhaus-micro-fastapi/actions/workflows/ci.yml/badge.svg)](https://github.com/chrdio/api-funkhaus-micro-fastapi/actions/workflows/ci.yml)

![cover](https://user-images.githubusercontent.com/83789452/190855163-cf024491-9399-4295-8645-dfa9288b972d.png)

This gateway microservice for the progression generation pipeline:
- uses the **pydantic** library for robust data coercion, validation and serialization
- orchestrates the chord-progression generation pipeline asynchronously with the **aiohttp** library
- authorizes client requests with **FastAPI** and **starlette** middleware