# The Iris.ai test assignment

Built with Django 5.1 and Python 3.11. 
Python virtual env support is necessary to run app.

The repo cli is the `./run` script.
```text
$ ./run --help
Runs either app or tests.

Usage:
    ./run [COMMANDS] [OPTIONS] [EXTR_ARGS]

Commands:
    test           Run tests
    e2e-test       Run e2e tests

Options:
    --dev          Run dev server
    --profile FILE Load wall profiles into database from file before run server
    --workers NUM  Set the number of workers for multi process case (default: 1)
    --debug        Set bash 'x' option
    --help         Shows help message

For extra Django CLI use 'python3 /home/q/work/irisai/src/manage.py'
```

To run integration tests issue

```text
$ ./run test
```

To run end-to-end tests the line is as follows. 
I ran into that Django test client and the infrastructure behind it 
as turns out sometimes behaves differently compared to real app. 
So after making integration tests I decided to add real e2e tests 
to be sure that the app works as necessary.
Docker and docker compose are mandatory to have to run these tests.
To install it on Ubuntu: `wget -qO- https://get.docker.com | sudo bash`

```
$ ./run e2e-test
```

To run app on top of the gunicorn
```
$ ./run
```


To run app dev server
```
$ ./run --dev
```

To import profile before server run
```
$ ./run --profile wall-profiles.txt
```

To import profile and set number of workers before run server
```text
./run --profile e2e-tests/wall-profiles2.txt --workers 5
```

Endpoints
```text
/profiles/<int:proflie_id>/days/<int:day>/
/profiles/<int:proflie_id>/overview/<int:day>/
/profiles/overview/<int:day>/
/profiles/overview/
```
For multiprocess version endpoints are
```text
/mp/profiles/<int:proflie_id>/days/<int:day>/
/mp/profiles/<int:proflie_id>/overview/<int:day>/
/mp/profiles/overview/<int:day>/
/mp/profiles/overview/
```
