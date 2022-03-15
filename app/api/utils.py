from typing import Any, Dict, List

import requests
from sqlalchemy import and_, create_engine, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.database import engine
from app.models import Rate


async def convert_currency(**kwargs: Dict[str, Any]) -> float:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        query = """
            WITH a AS (
                SELECT rate AS to_rate
                FROM rate
                WHERE currency='%s'
            ),
            b AS (
                SELECT ((a.to_rate / rate.rate) * %f) AS converted_amount
                FROM a, rate
                WHERE rate.currency='%s'
            )
            SELECT * FROM b;
        """ % (
            kwargs["to"],
            kwargs["amount"],
            kwargs["from_"],
        )
        result = await session.execute(text(query))
    return round(result.scalar_one(), 2)


def load_curreny():
    url = "%slatest?access_key=%s&format=1" % (settings.FX_API_URL, settings.FX_API_KEY)
    response: requests.Response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        session = sessionmaker(create_engine("sqlite:///./database.db"))
        print("about processing")
        with session() as session:
            _filter = list(
                map(
                    lambda item: and_(
                        Rate.rate != data["rates"][item], Rate.currency == item
                    ),
                    data["rates"],
                )
            )
            stmt = select(Rate).filter(or_(*_filter))
            result = session.execute(stmt)
            rates: List[Rate] = result.scalars().all()
            print(len(rates))
            if rates:
                for rate in rates:
                    rate.base = data["base"]
                    rate.date = data["date"]
                    rate.rate = data["rates"][rate.currency]
                    session.add(rate)
            else:
                if session.execute(text("SELECT * FROM rate;")).first() is None:
                    print("rewriting")
                    for rate, fx in data["rates"].items():
                        rate = Rate(
                            base=data["base"], date=data["date"], currency=rate, rate=fx
                        )
                        session.add(rate)

            if session.dirty or session.new:
                print("updated")
                session.commit()


# load_curreny()
