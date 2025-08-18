import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


# The parent class for all database model classes.
# This holds settings that are common to all the tables.
class Model(DeclarativeBase):
    pass


load_dotenv()

print(f"Database URL: {os.environ['DATABASE_URL']}")

# The engine manages connections to a database.
# Some nice to know options are:
#   echo = True, to have SQLAlchemy log every SQL statement
#   pool_size=<N>, set a custom size for the connection pool (default 5)
#   max_overflow=<N>, max number of connections that can be created during spikes (default 10)
engine = create_engine(os.environ["DATABASE_URL"], echo=True)
