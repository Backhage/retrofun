# The third set of exercises are listed below

Solutions are my own and there might be better ways to solve it them.

## Exercises

Start a Python session and write queries that return the following information:

1. Products that were made in the UK or USA.
2. Products not made in UK or USA. Products that were made in UK and/or USA
   jointly with other countries should be included in the query results.
3. Countries with products based on the Z80 CPU or any of its clones.
4. Countries that had products made in the 1970s in alhpabetical order.
5. The 5 countries with the most products. If there is a tie, the query should
   pick the countries in alphabetical order.
6. Manufacturers that have more than 3 products in UK or USA.
7. Manufacturers that have products in more than one country.
8. Products made jointly in UK and USA.

## Solutions

Here are the current table models for reference:

```python

ProductCountry = Table(
    "products_countries",
    Model.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True, nullable=False),
    Column("country_id", ForeignKey("countries.id"), primary_key=True, nullable=False),
)

class Product(Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)  
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id"), index=True
    )
    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="products")
    year: Mapped[int] = mapped_column(index=True)
    countries: Mapped[list["Country"]] = relationship(
        secondary=ProductCountry, back_populates="products"
    )
    cpu: Mapped[Optional[str]] = mapped_column(String(32))


class Manufacturer(Model):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    products: Mapped[list["Product"]] = relationship(
        back_populates="manufacturer", cascade="all, delete-orphan"
    )


class Country(Model):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True, unique=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=ProductCountry, back_populates="countries"
    )

```

1. Take advantage of the mapping table `product_countries` to select products
   where UK or USA is in the list of the product countries. Use `distinct` to
   ensure products made in both UK and USA does not appear multiple times.

   ```python
   from sqlalchemy import select
   from db import Session
   from models import Product, Country

   session = Session()
   q = (select(Product)
        .join(Product.countries)
        .where(Country.name.in_(["UK", "USA"]))
        .distinct())

   session.scalars(q).all()

   """
   [Product(74, "Honeywell 316"), Product(16, "Apple II"),
    Product(35, "Bally Astrocade"), Product(39, "PET"),
    Product(78, "Compucolor II"),
    ...
    Product(32, "Atari TT"), Product(76, "IBM PS/1"), Product(33, "Falcon"),
    Product(6, "A7000")]
   """
   ```
