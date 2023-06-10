from functools import partial
from multiprocessing import Pool, cpu_count

import typer
from alembic import command as alembic

from ironbot import scrappers
from ironbot.db import Database
from ironbot.models import Title
from ironbot.settings import Settings


db = typer.Typer()
app = typer.Typer()
app.add_typer(db, name="db", help="Manage the database")


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
    events = dict(enumerate(scrappers.event_names(data), 1))
    event = events.get(event_number)
    if not event:
        raise RuntimeError(f"Event number {event_number} not found.")

    for athlete in scrappers.start_list(data, event):
        print(athlete)


def save_start_list(data, name):
    settings = Settings()
    db = Database(settings.database_url)
    athletes = scrappers.start_list(data, name)
    return db.save_athletes(athletes), name


@db.command()
def init() -> None:
    """Start a database for scratch. Requires DATABASE_URL environment
    variable. Run migrations, scrap events and start lists and persist them in
    the database."""
    settings = Settings()
    db = Database(settings.database_url)

    print("==> Creating database and running migrations…")
    alembic.upgrade(settings.alembic, "head")

    print("==> Loadign events…")
    data = scrappers.load(Title.CALENDAR)

    count = db.save_events(scrappers.events(data))
    print(f"==> Saved {count} events.")

    print("==> Loading start lists…")
    data = scrappers.load(Title.START_LIST)
    with Pool(processes=cpu_count()) as pool:
        names = scrappers.event_names(data)
        save_athletes = partial(save_start_list, str(data))
        for result, name in pool.imap_unordered(save_athletes, names):
            print(f"==> Saved {result} athletes from {name} start list.")


@db.command()
def migration(name: str) -> None:
    """Create a new migration."""
    settings = Settings()
    alembic.revision(settings.alembic, name, autogenerate=True)


@db.command()
def migrate(version: str = "head") -> None:
    """Runs pending migration."""
    settings = Settings()
    alembic.upgrade(settings.alembic, version)
