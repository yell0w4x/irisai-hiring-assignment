# The Iris.ai test assignment

The repo cli is the `./run` script.
```text
$ ./run --help
Run app dev server or tests.

Usage:
    ./run [COMMANDS] [OPTIONS]

Commands:
    test           Run tests

Options:
    --profile FILE Load wall profiles into database from file before run server
    --debug        Set bash 'x' option
    --help         Shows help message

For extra Django CLI use 'python3 /home/q/work/irisai/src/manage.py'
```

To run tests issue

```
$ ./run test
```

To run app dev server
```
$ ./run
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