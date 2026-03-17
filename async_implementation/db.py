import os
from dotenv import load_dotenv
from sqlalchemy import MetaData, event, inspect
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Model(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


load_dotenv()

engine = create_async_engine(os.environ["DATABASE_URL"])
Session = async_sessionmaker(engine, expire_on_commit=False)
"""Setting expire_on_commit to False disables a default SQLAlchemy
behavior that marks models as expired after the session is committed.
Models that are marked as expired are implicitly refreshed from a
database query when any of its attributes are accessed again. Since
implicit database activity cannot occur in an asynchronous application,
expired objects should not be used.
"""


@event.listens_for(Model, "init", propagate=True)
def init_relationships(tgt, arg, kw):
    """This event listener triggers when a new Model is instantiated.
    The function initializes the relationships of the new object which
    helps avoid triggering lazy load (which throws a greenlet exception
    in asynchronous context) in the case the object has a list style
    relationship that has not been initialized, the session is flushed,
    after which the list style attribute is accessed.
    """
    mapper = inspect(tgt.__class__)
    for arg in mapper.relationships:
        if arg.collection_class is None and arg.uselist:
            continue  # skip write-only and similar relationships
        if arg.key not in kw:
            kw.setdefault(
                arg.key, None if not arg.uselist else arg.collection_class())
