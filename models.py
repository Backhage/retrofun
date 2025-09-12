from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Model


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
    country: Mapped[Optional[str]] = mapped_column(String(32))
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
    products: Mapped[list["Product"]] = relationship(back_populates="manufacturer")

    def __repr__(self):
        return f'Manufacturer({self.id}, "{self.name}")'
