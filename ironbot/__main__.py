from typing import Optional

import typer

import ironbot

app = typer.Typer()


@app.command()
def calendar() -> None:
    data = ironbot.load(ironbot.Title.CALENDAR)
    for event in ironbot.events(data):
        print(event)


@app.command()
def list_events() -> None:
    data = ironbot.load(ironbot.Title.START_LIST)
    print("Please, choose one of the followign events:")
    for number, name in enumerate(ironbot.event_names(data), 1):
        print(f" [{number}] {name}")
    return


@app.command()
def start_list(event_number: int) -> None:
    data = ironbot.load(ironbot.Title.START_LIST)
    print(   ironbot.start_list(data, event_number))


if __name__ == "__main__":
    app()
