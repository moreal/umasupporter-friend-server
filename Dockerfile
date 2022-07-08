FROM python:3.10-buster as builder

ENV POETRY_VERSION=1.1.13
RUN python3 -m pip install poetry==$POETRY_VERSION

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project true --local
RUN poetry install --no-dev

FROM python:3.10-buster as runtime

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY app /app/app

EXPOSE 8000

ENTRYPOINT ["uvicorn", "app:app", "--port", "8000"]
