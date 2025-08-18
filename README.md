# What this repo contains

When working with database backed Python applications I soon realized that I
lacked knowledge with SQLAlchemy. To fix this, I introduced daily 30 minute
sessions where I read the book SQLAlchemy 2 In Practice and followed along with
the implementation.

This repository contains the code I wrote and notes taken while following along
in the book.

## Technical decisions

SQLAlchemy supports multiple different databases. I choose to use SQLite due to
its simplicity, that Python has built in support for it and because it doesn't
require a separate server to run.

The SQLAlchemy library consists of two modules called Core and ORM. An
application can use Core only, or take advantage of the ORM module. The approach
taken here is the combined approach where both the Core and the ORM functionality
is being used.
