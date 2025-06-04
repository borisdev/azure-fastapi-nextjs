FROM python:3.12-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="/opt/poetry" \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"
    # reminder of what is inside VENV_PATH: 
    # /opt/pysetup/.venv/bin/fastapi

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


# builder-base is used to build dependencies for building the app
FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=2.1.1
RUN curl -sSL https://install.python-poetry.org | python3 -

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./README.md ./
COPY ./website ./website
# install runtime dependencies including the local package
RUN poetry install --only main

CMD ["tail", "-f", "/dev/null"]


FROM python-base as production
ENV FASTAPI_ENV=production
# COPY --from=builder-base /opt/pysetup/.venv/bin/fastapi /opt/pysetup/.venv/bin/fastapi
# just copy our runtime dependencies from the builder-base, and skip those for building
COPY --from=builder-base $VENV_PATH $VENV_PATH

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
# RUN poetry install --only root....NO NEED SINCE WE COPY THE VENV FROM BUILDER-BASE

COPY ./website /website
WORKDIR /website

ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD ["fastapi", "run", "--workers", "4", "website/main.py"]
EXPOSE 80
