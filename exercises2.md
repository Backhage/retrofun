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
