from asyncio import gather, run

import typer
from alembic import command as alembic
from httpx import AsyncClient

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
    client = AsyncClient()
    data = run(scrappers.load(client, Title.CALENDAR))
    events = run(scrappers.events(client, data))
    for event in events:
        print(event)


@app.command()
def start_lists() -> None:
    """List upcoming Ironman professional races with start list available, with
    a unique number for each one (to be used in the `start-list` command)."""
    data = run(scrappers.load(AsyncClient(), Title.START_LIST))
    print("Choose one of the followign events to use with `start-list` command:")
    events = scrappers.event_names(data)
    for number, name in enumerate(events, 1):
        print(f" [{number}] {name}")
    return


@app.command()
def start_list(event_number: int) -> None:
    """Gets the start list for an Ironman professional race (use `start-lists`
    to get the event number)."""
    client = AsyncClient()
    data = run(scrappers.load(client, Title.START_LIST))
    events = dict(enumerate(scrappers.event_names(data), 1))
    event = events.get(event_number)
    if not event:
        raise RuntimeError(f"Event number {event_number} not found.")

    start_lists = run(scrappers.start_list(client, data, event))
    for athlete in start_lists:
        print(athlete)


@db.command()
def init() -> None:
    """Start a database for scratch. Requires DATABASE_URL environment
    variable. Run migrations, scrap events and start lists and persist them in
    the database."""
    settings = Settings()
    db = Database(settings.database_url)

    print("==> Creating database and running migrations…")
    alembic.upgrade(settings.alembic, "head")

    async def save_start_list(client, data, name) -> None:
        await scrappers.start_list(client, data, name)
        count = db.save_athletes(await scrappers.start_list(client, data, name))
        print(f"==> Saved {count} athletes in {name} start_list.")

    async def wrapper() -> None:
        client = AsyncClient()
        print("==> Loadign events…")
        data = await scrappers.load(client, Title.CALENDAR)

        events = await scrappers.events(client, data)
        count = db.save_events(events)
        print(f"==> Saved {count} events.")

        print("==> Loading start lists…")
        data = await scrappers.load(client, Title.START_LIST)
        names = tuple(scrappers.event_names(data))
        futures = (save_start_list(client, data, name) for name in names)
        await gather(*futures)

    run(wrapper())


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
