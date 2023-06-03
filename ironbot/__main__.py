import typer

from ironbot import scrappers
from ironbot.models import Title

app = typer.Typer()


@app.command()
def calendar() -> None:
    """List the details of the upcoming Ironman professional races."""
    data = scrappers.load(Title.CALENDAR)
    for event in scrappers.events(data):
        print(event)


@app.command()
def start_lists() -> None:
    """List upcoming Ironman professional races with start list available, with
    a unique number for each one (to be used in the `start-list` command)."""
    data = scrappers.load(Title.START_LIST)
    print("Choose one of the followign events to use with `start-list` command:")
    for number, name in enumerate(scrappers.event_names(data), 1):
        print(f" [{number}] {name}")
    return


@app.command()
def start_list(event_number: int) -> None:
    """Gets the start list for an Ironman professional race (use `start-lists`
    to get the event number)."""
    data = scrappers.load(Title.START_LIST)
    for athlete in scrappers.start_list(data, event_number):
        print(athlete)
