# The fourth set of exercises are listed below

Solutions are my own and there might be better ways to solve it them.

## Exercises

Start a Python session and write queries that return the following information:

1. Orders above $300 in descending ordered by the sale amount from highest to lowest.
2. Orders that include one or more ZX81 computers.
3. Orders that include a product made by Amstrad.
4. Orders made on the 25th of December 2022 with two or more line items.
5. Customers with their first and last order date and time. Hint: the min() and
   max() functions can help with this query.
6. The top 5 manufacturers that had the most sale amounts, sorted by those amounts
   in descending order.
7. Products, their average star rating and their review count, sorted by review count
   in descending order.
8. Products and their average star rating, but only counting reviews that include
   a written comment.
9. Average star rating for the Commodore 64 computer in each month of 2022.
10. Customers with the minimum and maximum star rating they gave to a product,
    sorted alphabetically by customer name.
11. Manufacturers with their average star rating, sorted from highest to lowest
    rating.
12. Product countries with their average star rating, sorted from highest to lowest
    rating.

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

    order_items: WriteOnlyMapped["OrderItem"] = relationship(back_populates="product")

    reviews: WriteOnlyMapped["ProductReview"] = relationship(back_populates="product")

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


class Country(Model):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True, unique=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=ProductCountry, back_populates="countries"
    )

    def __repr__(self):
        return f'Country({self.id}, "{self.name}")'


class Order(Model):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.id"), index=True)
    customer: Mapped["Customer"] = relationship(back_populates="orders")

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

    def __repr__(self):
        return f"Order({self.id.hex})"


class Customer(Model):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    address: Mapped[str | None] = mapped_column(String(128))
    phone: Mapped[str | None] = mapped_column(String(32))

    orders: WriteOnlyMapped["Order"] = relationship(back_populates="customer")
    product_reviews: WriteOnlyMapped["ProductReview"] = relationship(
        back_populates="customer"
    )

    def __repr__(self):
        return f'Customer({self.id.hex}), "{self.name}"'


class OrderItem(Model):
    __tablename__ = "orders_items"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"), primary_key=True)

    product: Mapped["Product"] = relationship(back_populates="order_items")
    order: Mapped["Order"] = relationship(back_populates="order_items")

    unit_price: Mapped[float]
    quantity: Mapped[int]


class ProductReview(Model):
    __tablename__ = "product_reviews"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id"), primary_key=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )
    rating: Mapped[int]
    comment: Mapped[str | None] = mapped_column(Text)

    product: Mapped["Product"] = relationship(back_populates="reviews")
    customer: Mapped["Customer"] = relationship(back_populates="product_reviews")
```

1. Summarize the orderitems for each order and sort the orders by the total order
   value.

   ```python
   from sqlalchemy import select, func
   from db import Session
   from models import Order, OrderItem

   session = Session()

   order_value = func.sum(OrderItem.unit_price * OrderItem.quantity).label(None)

   q = (select(Order, order_value)
        .join(OrderItem)
        .group_by(Order)
        .having(order_value > 300)
        .order_by(order_value.desc()))

   session.execute(q).all()

   """
   [(Order(2ecc133772174bb7a2d5be22c122a469), 463.99),
    (Order(b6bebc250a184541a2736d2d729a6eef), 461.51),
    ...
    (Order(aa772b99e41a4ef5af9583ea81c192a7), 300.19)]
   """
   ```

2. Here we need to join Order, OrderItem, and Product and filter on the product
   name.

   ```python
   from sqlalchemy import select
   from db import Session
   from models import Order, OrderItem, Product

   session = Session()

   q = (select(Order)
        .join(Order.order_items)
        .join(OrderItem.product)
        .where(Product.name == "ZX81"))

   session.scalars(q).all()

   """
   [Order(0f6c3d09b21a4119b521c9232447f58c),
   Order(18ba8557d5054438b9b5912ee783960c),
   Order(61090d1d9f9e4d5f858d70da5031e6fb)]
   """
   ```
