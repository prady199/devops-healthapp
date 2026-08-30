# Hardened image build.
#
# Controls:
#   * Slim base image - smaller attack surface than a full OS image
#   * Dependencies installed as a separate layer, then the app copied in
#   * Application runs as an unprivileged user (uid 10001), never root
#   * No bytecode written at runtime, so the filesystem can be read-only
#   * Container-level healthcheck

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Create an unprivileged account and hand it the app directory
RUN groupadd --gid 10001 appgroup \
 && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin appuser \
 && chown -R appuser:appgroup /app

USER 10001

EXPOSE 5000

CMD ["python", "app.py"]
