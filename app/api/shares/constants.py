from enum import Enum
from functools import reduce

from sqlalchemy import create_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from app.models import Rate


def get_currencies():
    session = sessionmaker(create_engine("sqlite:///./database.db"))
    with session() as session:
        stmt = select(Rate.currency)
        result = session.execute(stmt)
        data = result.scalars().all()
    return reduce(lambda x, y: {**x, y: y}, data, {})


currencies = get_currencies()
Currency = Enum("Currency", currencies)
