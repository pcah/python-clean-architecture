ARG POETRY_VERSION=1.1.7
ARG PYTHON_VERSION=latest
ARG IMAGE_BASE=-slim
ARG IMAGE_VERSION=python:${PYTHON_VERSION}${IMAGE_BASE}
ARG WORKSPACE="/workspace"

# TODO decide whether download get-poetry.py or install it via PyPI
# FROM debian:stable-slim as downloader
# ARG WORKSPACE
# WORKDIR ${WORKSPACE}
# RUN apt update -y \
#     && apt install -y --no-install-recommends \
#     ca-certificates \
#     curl \
#     && rm -rf /var/lib/apt/lists/*
# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py > /get-poetry.py

FROM ${IMAGE_VERSION} AS dev
ARG IMAGE_VERSION
ARG POETRY_VERSION
ARG PYTHON_VERSION
ARG WORKSPACE
ENV DEBIAN_FRONTEND=noninteractive \
    IMAGE_VERSION=${IMAGE_VERSION} \
    PATH="${PATH}:/root/.poetry/bin" \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=${POETRY_VERSION} \
    WORKSPACE=${WORKSPACE}
WORKDIR ${WORKSPACE}
RUN apt update -y \
    && apt install -y --no-install-recommends \
    git \
    libpython3-dev \
    tree \
    vim \
    && rm -rf /var/lib/apt/lists/*
# COPY --from=downloader /get-poetry.py .
RUN pip install -U \
    pip \
    poetry==${POETRY_VERSION} \
    setuptools \
    && poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction
ENTRYPOINT [ "/bin/bash" ]

FROM dev AS test
ENTRYPOINT [ "pytest", "--cov", "--cov-report", "term", "--cov-report", "xml"]

FROM dev AS lint
COPY .git .git
COPY .pre-commit-config.yaml .
RUN pre-commit install --install-hooks
ENTRYPOINT [ "pre-commit", "run", "-a" ]
