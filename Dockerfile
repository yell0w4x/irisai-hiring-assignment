FROM python:3.11-bullseye

WORKDIR /app
COPY src /app/src
COPY run requirements.txt /app
COPY e2e-tests/wall-profiles1.txt e2e-tests/wall-profiles2.txt /app
CMD ['/app/run']
