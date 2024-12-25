from sqlalchemy import create_engine, select, insert, update, delete
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)

Base = declarative_base()

def query(self, *args):
    return select(self.__class__, *args)

def execute(self, query):
    with engine.connect() as conn:
        data = []

        for row in conn.execute(query):
            data.append(row._asdict())

        return data

def save(self):
    with engine.connect() as conn:
        stmt = insert(self.__class__)

        if (type(self.id) == int):
            stmt = update(self.__class__).where(self.id == self.id)

        conn.execute(stmt.values(
            **{ key: value for key, value in self.__dict__.items() if key.startswith('_') == False })
        )

        conn.commit()

def remove(self):
    with engine.connect() as conn:
        conn.execute(
            delete(self.__class__).where(
                self.id == self.id
            )
        )

        conn.commit()

Base.query = query
Base.get = execute
Base.save = save
Base.delete = remove

def init_db():
    from .models.report import Report

    Base.metadata.create_all(bind=engine)
