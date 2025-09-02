# The first set of exercises are listed below

Solutions are my own and there might be better ways to solve it them.

## Exercises

Start a Python session and write queries that return the following information:

1. The first three products in alphabetical order built in the year 1983.
2. Products that use the "Z80" CPU or any of its cloes. Assume that all products
based on this CPU have the word "Z80" in the `cpu` column.
3. Products that use either the "Z80" or the "6502" CPUs, or any of its clones,
built before 1990, sorted alphabetically by name.
4. The manufacturers that built products in the 1980s.
5. Manufacturers whose names start with the letter "T", sorted alphabetically.
6. The first and last years in which products have been built in Croatia, along
with the number of products built.
7. The number of products that were built each year. The results should start from
the year with the most products, to the year with the least. Years in which no
products were built do not need to be included.
8. The number of manufacturers in the United States (note that the `country` field
for these products is set to `USA`)

## Solutions

Here is the current model for reference:

```python
class Product(Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    manufacturer: Mapped[str] = mapped_column(String(64), index=True)
    year: Mapped[int] = mapped_column(index=True)
    country: Mapped[Optional[str]] = mapped_column(String(32))
    cpu: Mapped[Optional[str]] = mapped_column(String(32))
```

1. Order the products by `name` then take the top 3 where `year` equals 1983.

```python
from sqlalchemy import select

from db import Session
from models import Product

session = Session()
q = select(Product).order_by(Product.name).where(Product.year == 1983).limit(3)
session.scalars(q).all()

"""
[Product(17, "Apple IIe"), Product(85, "Aquarius"), Product(26, "Atari 1200XL")]
"""

```
