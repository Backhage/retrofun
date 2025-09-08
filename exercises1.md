# The first set of exercises are listed below

Solutions are my own and there might be better ways to solve it them.

## Exercises

Start a Python session and write queries that return the following information:

1. The first three products in alphabetical order built in the year 1983.
2. Products that use the "Z80" CPU or any of its clones. Assume that all products
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

2. Use the `like` function to get products that include "Z80" in the `cpu` column.

    ```python
    # Imports and session like in exercise 1

    q = select(Product).where(Product.cpu.like("%Z80%"))
    session.scalars(q).all()

    """
    [Product(7, "CPC 464"), Product(8, "CPC 664"), Product(9, "CPC 6128"),
     Product(10, "464 Plus"), Product(11, "6128 Plus"), Product(12, "PCW"),
     Product(23, "CT-80"), Product(34, "Bally Brain"), Product(35, "Bally Astrocade"),
     Product(36, "CoBra"), Product(37, "Lynx"), Product(38, "Coleco Adam"),...]
    """
    ```

3. Use `like` with `or_` to select the CPUs, then `where` to filter out those
   built before 1990, and finally `order_by` to sort in alphabetical order.

    ```python
    # Imports similar to before but add...
    from sqlalchemy import or_

    q = (select(Product)
         .where(or_(Product.cpu.like("%Z80%"), Product.cpu.like("%6502%")))
         .where(Product.year < 1990)
         .order_by(Product.name))

    session.scalars(q).all()

    """
    [Product(84, "ABC 80"), Product(1, "Acorn Atom"), Product(55, "Alpha"),
     Product(16, "Apple II"), Product(20, "Apple II Plus"), Product(17, "Apple IIe"),
     Product(85, "Aquarius"), Product(26, "Atari 1200XL"), Product(30, "Atari 130XE"),
     Product(24, "Atari 400"), Product(27, "Atari 600XL"), Product(29, "Atari 65XE"),
     Product(25, "Atari 800"),...]
    """
    ```

4. Select the manufacturer column where year is greater than or equal 1980
   and less than 1990. Ensure distinct.

    ```python
    # Imports like before

    q = (select(Product.manufacturer)
         .where(Product.year >= 1980)
         .where(Product.year < 1990)
         .distinct())

    session.scalars(q).all()

    """
    ['Acorn Computers Ltd', 'Commodore', 'Data Applications International', 'EACA',
     'Radio Shack', 'Philips', 'Pravetz', 'Sinclair Research', 'NEC Home Electronics',
     'NEC', 'PEL Varaždin', ...]
    """
    ```

5. Select the manufacturer column and use `like` to get those that starts with
   `T` and order_by to get them in alphabetical order. Make sure they are distinct.

    ```python
    # Imports like before

    q = (select(Product.manufacturer)
         .where(Product.manufacturer.like('T%'))
         .order_by(Product.manufacturer)
         .distinct())

    session.scalars(q).all()

    """
    ['Tangerine Computer Systems', 'Technosys', 'Tesla', 'Texas Instruments',
     'Thomson', 'Timex Sinclair', 'Tomy', 'Tsinghua University']
    """
    ```

6. Use `func.min`, `func.max`, `func.count` to get min, max, and count of the
   products.

    ```python
    # Imports like before, but also import func
    from sqlalchemy import func

    q = (select(func.min(Product.year), func.max(Product.year), func.count())
         .where(Product.country == 'Croatia'))

    r = session.execute(q)
    r.first()

    """
    (1981, 1984, 4)
    """
    ```
