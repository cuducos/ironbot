# `ironbot` [![Tests](https://github.com/cuducos/ironbot/actions/workflows/tests.yml/badge.svg)](https://github.com/cuducos/ironbot/actions/workflows/tests.yml)

## Requirements

 `ironbot` depends on Python 3.9 or newer, and on [Camelot, which requires `ghostscript`](https://camelot-py.readthedocs.io/en/master/user/install-deps.html).

## Install

```console
$ pip install ironbot
```

## Usage

```console
$ ironbot --help
Usage: ironbot [OPTIONS] COMMAND [ARGS]...
Commands:
  calendar     List the details of the upcoming Ironman professional races.
  start-list   Gets the start list for an Ironman professional race (use...
  start-lists  List upcoming Ironman professional races with start list...
```

### Exemples

#### Details of upcoming Ironman professional races

```console
$ ironbot calendar
2023-06-04	IRONMAN Hamburg - MPRO European Championship	$75,000	5MPRO	CLOSED	CLOSED
2023-06-10	IRONMAN 70.3 Boulder	$50,000	2MPRO/2WPRO	CLOSED	CLOSED
2023-06-11	IRONMAN 70.3 Warsaw	$15,000	2MPRO/2WPRO	CLOSED	CLOSED
…
```

#### List events with start list available

```console
$ ironbot start-lists
Choose one of the followign events to use with `start-list` command:
 [1] 2023 IRONMAN European Championship Hamburg
 [2] 2023 IRONMAN 70.3 Boulder
 …
```

#### Get the start list of an event

```console
$ ironbot start-list 4
1	Daniela Ryf	CHE (Switzerland)
3	Ashleigh Gentle	AUS (Australia)
4	Anne Reischmann	DEU (Germany)
…
```

#### Save all data in a database

Requires an environment variable `DATABASE_URL` with a valid [SQLAlchemy connection string](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls).

```console
$ ironbot db init
```

## Contributing

Make sure that all tests pass:

```console
$ poetry run pytest
```
