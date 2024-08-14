FROM python:3.11-bullseye

RUN cd /tmp && wget https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_amd64.deb
RUN apt-get install /tmp/dumb-init_1.2.5_amd64.deb

WORKDIR /test
COPY e2e-tests/requirements.txt /test/requirements.txt
RUN pip install -r requirements.txt
COPY e2e-tests/src /test/
COPY e2e-tests/wait-for-it.sh /test/

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["pytest"]
