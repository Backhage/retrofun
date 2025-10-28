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

2. Use the `not_` functionality to invert the query from 1. Since there is an
   entry for each product/country combination in the join table any products
   that were made jointly with another country should be included in the
   results.

   ```python
   from sqlalchemy import select, not_
   from db import Session
   from models import Product, Country

   session = Session()
   q = (select(Product)
        .join(Product.countries)
        .where(not_(Country.name.in_(["UK", "USA"])))
        .distinct())

   session.scalars(q).all()

   """
   [Product(55, "Alpha"), Product(56, "Beta"), Product(57, "Gama"),
    Product(134, "PMD 85"), Product(135, "MAŤO"),
    Product(50, "DAI Personal Computer"),
    ...
    Product(148, "West PC-800"), Product(84, "ABC 80"), Product(104, "Euro PC")]
   """
   ```

3. Join country with products and selects those products that have CPUs that
   have Z80 in its name. Make sure only distinct countries are listed.

   ```python
   from sqlalchemy import select
   from db import Session
   from models import Country, Product

   session = Session()

   q = (select(Country)
        .join(Country.products)
        .where(Product.cpu.like("%Z80%"))
        .distinct())

   session.scalars(q).all()

   """
   [Country(8, "Czechoslovakia"), Country(7, "Belgium"), Country(5, "Romania"),
    Country(22, "Portugal"), Country(16, "Australia"), Country(4, "Netherlands"),
    Country(3, "USA"), Country(12, "Brazil"), Country(24, "Hungary"),
    Country(21, "East Germany"), Country(1, "UK"), Country(23, "Poland"),
    Country(9, "USSR"), Country(11, "Japan"), Country(6, "Hong Kong"),
    Country(25, "Norway"), Country(14, "Sweden")]
   """
   ```

4. Again join country with products and select those products where year is
   in the range 1970 to 1979. Group by country and order by country name.

   ```python
   from sqlalchemy import select, and_
   from db import Session
   from models import Country, Product

   session = Session()

   q = (select(Country)
        .join(Country.products)
        .where(and_(Product.year >= 1970, Product.year <= 1979))
        .group_by(Country)
        .order_by(Country.name))

   session.scalars(q).all()

   """
   [Country(11, "Japan"), Country(14, "Sweden"), Country(3, "USA")]
   """
   ```

5. Select Country, use the count function to count the number of products for
   each country and order by that count. Also order by Country name to get the
   alphabetical ordering right for countries where the product count is equal.

   ```python
   from sqlalchemy import select, func
   from db import Session
   from models import Country, Product

   session = Session()
   
   q = (select(Country)
        .join(Country.products)
        .group_by(Country)
        .order_by(func.count(Product.id).desc(), Country.name)
        .limit(5))

   sessions.scalars(q).all()

   """
   [(Country(3, "USA"),), (Country(1, "UK"),), (Country(11, "Japan"),),
   (Country(6, "Hong Kong"),), (Country(22, "Portugal"),)]
   """
   ```
