# The Iris.ai test assignment

Built with Django 5.1 and Python 3.11. 
Python virtual env support is necessary to run app.

The repo cli is the `./run` script.
```text
$ ./run --help
Runs either app or tests.

Usage:
    ./run [COMMANDS] [OPTIONS] [EXTR_ARGS]

    All EXTR_ARGS are passed over to pytest, uvicorn or manage.py runserver.

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
To install it on Ubuntu: `wget -qO- https://get.docker.com | sudo bash`, 
for Arch based: `sudo pacman -S docker docker-buildx docker-compose`.
Add current user to docker group `adduser $USER docker` then reboot or issue this in terminal
`sudo -i -u $USER`.

```
$ ./run e2e-test
```

To run app on top of the uvicorn
```
$ ./run
```


To run app dev server
```
$ ./run --dev
```

Please note that multi process version uses async handlers. 
For some reason dev server sometimes gives Internal Server Error 
for first request to `/mp` API after start.


To import profile before server run
```
$ ./run --profile wall-profiles.txt
```

To import profile and set number of workers before run server
```text
$ ./run --profile e2e-tests/wall-profiles2.txt --workers 5
```

Endpoints
```text
/profiles/<int:proflie_id>/days/<int:day>/
/profiles/<int:proflie_id>/overview/<int:day>/
/profiles/overview/<int:day>/
/profiles/overview/
```

## Multi process version

For multiprocess version endpoints are
```text
/mp/profiles/<int:proflie_id>/days/<int:day>/
/mp/profiles/<int:proflie_id>/overview/<int:day>/
/mp/profiles/overview/<int:day>/
/mp/profiles/overview/
```

Worker logs will be available in `src/.log` folder.

Assignment has this stanza.

> The APIs should return the same results but each team that
> finishes a section instead of being relieved will move to the next section and the
> next wall profile if this is completed.

Actually it's bit unclear what means "same results". Conceptually API works in same way. 
But if we stick with idea that the amount of teams less then total sections
the daily related API will yield distinct values compared to the first case 
where the teams number equals total sections. 
In first case wall is always completed for not more than 30 days.
If teams number less than the total sections number the daily cost/ice 
amount breakdown differs from first variant as e.g. 2 teams each day complete 2 sections.
So the daily cost would be 390 * 1900.
Please note, I decided to stick with this approach in 
calculating daily expenses for the second part.
The final wall cost `/profiles/overview/` is the same for both variants.
