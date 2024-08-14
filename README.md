# The Iris.ai test assignment

Built with Django 5.1 and Python 3.11.

The repo cli is the `./run` script.
```text
$ ./run --help
Runs either app or tests.

Usage:
    ./run [COMMANDS] [OPTIONS]

Commands:
    test           Run tests
    e2e-test       Run e2e tests

Options:
    --dev          Run dev server
    --profile FILE Load wall profiles into database from file before run server
    --debug        Set bash 'x' option
    --help         Shows help message

For extra Django CLI use 'python3 /home/q/work/irisai/src/manage.py'
```

To run integration tests issue

```
$ ./run test
```

To run end-to-end tests the line is as follows. 
I ran into that Django test client and the infrastructure behind it 
as turns out sometimes behaves differently compared to real app. 
So after making integration tests I decided to add real e2e tests 
to be sure that the app works as necessary.

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

To import profile before run server
```
$ ./run --profile wall-profiles.txt
```

Endpoints
```text
/profiles/<int:proflie_id>/days/<int:day>/
/profiles/<int:proflie_id>/overview/<int:day>/
/profiles/overview/<int:day>/
/profiles/overview/
```