FROM python:3.13-slim

ENV UVICORN_LOOP=uvloop \
    UVICORN_HTTP=httptools

RUN apt-get update -y && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

WORKDIR /faithflow

COPY . /faithflow
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv venv && uv pip install .

ENV PATH="/faithflow/.venv/bin:$PATH"

CMD ["fastapi", "run", "--host", "0.0.0.0", "src/app.py"]
