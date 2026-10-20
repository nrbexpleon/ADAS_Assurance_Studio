FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY public ./public

ENV PYTHONPATH=/app/src \
    HOST=0.0.0.0 \
    PORT=8080

USER 65532:65532
EXPOSE 8080

CMD ["python", "-m", "adas_assurance.server"]
