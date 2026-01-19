import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# The parent class for all database model classes.
# This holds settings that are common to all the tables.
class Model(DeclarativeBase):
    metadata = MetaData(
        # Explicitly define naming conventions to avoid problems with
        # constraints getting unknown names assigned by the db.
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


load_dotenv()

print(f"Database URL: {os.environ['DATABASE_URL']}")

# The engine manages connections to a database.
# Some nice to know options are:
#   echo = True, to have SQLAlchemy log every SQL statement
#   pool_size=<N>, set a custom size for the connection pool (default 5)
#   max_overflow=<N>, max number of connections that can be created during spikes (default 10)
engine = create_engine(os.environ["DATABASE_URL"])

# The session maintains the list of new, read, modified, and deleted model instances
# Changes are passed on to the database in the context of a transaction when the
# session is flushed. When the session is committed the changes are permanently
# written to the db.
Session = sessionmaker(engine)
