# syntax=docker/dockerfile:1

FROM python:3.11-slim as build
WORKDIR /app

# See https://docs.docker.com/go/dockerfile-user-best-practices/
# to create a non-privileged user that the app will run under.

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt
COPY . .
CMD ["python", "-u", "main.py"]
