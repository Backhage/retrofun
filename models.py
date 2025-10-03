from typing import Optional

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Model

"""This is a join table used to describe a many-to-many relationship between
products and countries. The reason being that one product may have been developed
in multiple countries, and multiple products have been developed in the same
country.

Since this model is completely managed by SQLAlchemy the more simple construct
using `Table` and `Column` classes can be used instead of deriving a new class
from the `DeclarativeBase`.

This table does not have an `id` primary key, instead the two foreign keys are
marked as primary key. When multiple columns are designated as primary keys
SQLAlchemy creates a *composite* primary key (the primary key is the combination
of the two and it is that combination that must be unique).
"""
ProductCountry = Table(
    "products_countries",
    Model.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True, nullable=False),
    Column("country_id", ForeignKey("countries.id"), primary_key=True, nullable=False),
)


class Product(Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )  # Defaults to autoincrement starting from 1
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    # This defines a one-to-many relationship. Each manufacturer (the one) can
    # have many products (the many). This relationship is defined on the "many"
    # side of the model, in this case the Product.
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id"), index=True
    )
    # The `back_populates` relationship does not result in any information added
    # to the database, it is a strictly SQLAlchemy construction which allows for
    # SQLAlchemy to query the database when the `manufacturer` field is accessed
    # in the code.
    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="products")
    year: Mapped[int] = mapped_column(index=True)

    # The `secondary` argument tells SQLAlchemy that this relationship is supported
    # by a *secondary* table (the join table).
    countries: Mapped[list["Country"]] = relationship(
        secondary=ProductCountry, back_populates="products"
    )
    cpu: Mapped[Optional[str]] = mapped_column(String(32))

    def __repr__(self):
        return f'Product({self.id}, "{self.name}")'


class Manufacturer(Model):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    # As with the Product model, the `back_populates` relationship does not
    # result in any information added to the database. It only allows SQLAlchemy
    # to query the database for products for a given manufacturer when the `products`
    # field is accessed.
    #
    # Setting the cascade option to `all, delete-orphan` will set the behavior to
    # delete all products related to a manufacturer if a manufacturer is deleted.
    # The default is not to delete orphans which will cause an integrity error
    # throw an exception if attempted.
    products: Mapped[list["Product"]] = relationship(
        back_populates="manufacturer", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'Manufacturer({self.id}, "{self.name}")'


class Country(Model):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True, unique=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=ProductCountry, back_populates="countries"
    )

    def __repr__(self):
        return f'Country({self.id}, "{self.name}")'
