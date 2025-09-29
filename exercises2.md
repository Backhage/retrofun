# The second set of exercises are listed below

Solutions are my own and there might be better ways to solve it them.

## Exercises

Start a Python session and write queries that return the following information:

1. The list of products made by IBM and Texas Instruments.

2. Manufacturers that operate in Brazil.

3. Products that have a manufacturer that has the word "Research" in their name.

4. Manufacturers that made products based on the Z80 CPU or any of its clones.

5. Manufacturers that made products that are not based on the 6502 CPU or any
   of its clones.

6. Manufacturers and the year they went to market with their first product,
   sorted by year.

7. Manufacturers that have 3 to 5 products in the catalog.

8. Manufacturers that operated for more than 5 year.

## Solutions

Here are the current models for reference:

```python
class Product(Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)  
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id"), index=True
    )
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
    products: Mapped[list["Product"]] = relationship(
        back_populates="manufacturer", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'Manufacturer({self.id}, "{self.name}")'
```

1. Select `Product` and join on `Product.manufacturer`. Use `_or` to match against
   both IBM and Texas Instruments as manufacturer name.

    ```python
    from sqlalchemy import select, _or
    from db import Session
    from models import Product, Manufacturer

    session = Session()
    q = (select(Product)
         .where(or_(Manufacturer.name == "IBM", Manufacturer.name == "Texas Instruments"))
         .join(Product.manufacturer))

    session.scalars(q).all()

    """
    [Product(75, "PCjr"), Product(76, "IBM PS/1"),
     Product(132, "TI-99/4"), Product(133, "TI-99/4A")]
    """
    ```

2. Country is a column in the product table so `select` Manufacturer joined with
   products where the country field of the product is Brazil.

   ```python
   from sqlalchemy import select
   from db import Session
   from models import Product, Manufacturer

   session = Session()
   q = (select(Manufacturer)
        .where(Product.country == "Brazil")
        .join(Manufacturer.products))

   session.scalars(q).all()

   """
   [Manufacturer(32, "Gradiente"),
    Manufacturer(46, "Comércio de Componentes Eletrônicos"),
    Manufacturer(47, "Microdigital Eletronica"),
    Manufacturer(59, "Prológica")]
   """
   ```

3. Here `like` must be used to get the manufacturer(s) which names include the
   word Research. Wildcard character '%' is used to get any manufacturer that
   has the word Research no matter where in the name it exist.

   ```python
   from sqlalchemy import select
   from db import Session
   from models import Product, Manufacturer

   session = Session()
   q = (select(Product)
        .where(Manufacturer.name.like("%Research%"))
        .join(Product.manufacturer))

   session.scalars(q).all()

   """
   [Product(125, "ZX80"), Product(126, "ZX81"), Product(127, "ZX Spectrum"),
    Product(128, "Sinclair QL")]
   """
   ```

4. Since multiple products from the same manufacturer may be based on the Z80
   CPU the same manufacturer may appear many times in the result unless `distinct`
   is used to ensure each manufacturer is returned only once.

   ```python
   from sqlalchemy import select, distinct
   from db import Session
   from models import Product, Manufacturer

   session = Session()
   q = (select(Manufacturer)
        .distinct()
        .where(Product.cpu.like("%Z80%"))
        .join(Manufacturer.products))

   session.scalars(q).all()

   """
   [Manufacturer(2, "Amstrad"), Manufacturer(7, "Aster Computers"),
    Manufacturer(10, "Bally Consumer Products"), Manufacturer(11, "Brasov Computer"),
    Manufacturer(12, "Camputers"), Manufacturer(13, "Coleco"),
    Manufacturer(14, "Commodore"), Manufacturer(17, "Vtech"),
    ...
    Manufacturer(75, "West Computer AS"), Manufacturer(76, "GEM")]
   """
   ```

5. To select the products that are _not_ based on a specific CPU it can be
   negated by using the `not_` functionality. Otherwise the query is very
   similar to the one in task 4 above.

   ```python
   from sqlalchemy import select, distinct, not_
   from db import Session
   from models import Product, Manufacturer

   session = Session()
   q = (select(Manufacturer)
        .distinct()
        .where(not_(Product.cpu.like("%6502%"))) # Note the `not_`
        .join(Manufacturer.products))

   session.scalars(q).all()

   """
    [Manufacturer(1, "Acorn Computers Ltd"), Manufacturer(2, "Amstrad"),
     Manufacturer(4, "APF Electronics, Inc."), Manufacturer(5, "Apple Computer"),
     ...
     Manufacturer(74, "Videoton"), Manufacturer(76, "GEM")]
   """
   ```

6. Select Manufacturer and the minimum year of their respective product using
   the `func.min` function. To get each manufacturer just once, use `group_by`
   and to get the result sorted by the year of the product, use `order_by` with
   product year as the argument.

   ```python
   from sqlalchemy import select, func
   from db import Session
   from models import Product, Manufacturer

   session = Session()
   q = (select(Manufacturer, func.min(Product.year))
        .group_by(Manufacturer)
        .order_by(Product.year)
        .join(Manufacturer.products))

   session.execute(q).all() # Use execute since two values are wanted

   """
   [(Manufacturer(33, "Honeywell"), 1969), (Manufacturer(5, "Apple Computer"), 1977),
    (Manufacturer(10, "Bally Consumer Products"), 1977),
    (Manufacturer(14, "Commodore"), 1977)
    ...
    (Manufacturer(68, "Štátny majetok Závadka š.p."), 1989),
    (Manufacturer(37, "Intercompex"), 1990), (Manufacturer(22, "Dubna"), 1991)]
   """
   ```
