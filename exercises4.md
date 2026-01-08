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

3. Quite straight forward, but many joins.

   ```python
   from sqlalchemy import select
   from db import Session
   from models import Order, OrderItem, Product, Manufacturer

   session = Session()
 
   q = (select(Order)
        .join(Order.order_items)
        .join(OrderItem.product)
        .join(Product.manufacturer)
        .where(Manufacturer.name == "Amstrad")
        .distinct()

   session.scalars(q).all()

   """
   [Order(0a266278e4ba405db5a96d8d6848ac29), Order(3cf66503170f462cad94634731807017),
   Order(549f670fa3d64375aba19554a114b45c), Order(5624f45b9d134bb7933b71db4b7d9f79),
   ...
   Order(7b46a2824e1c4a45b8d015ab5355a05b), Order(d5cf91faaf3e45219d2a426264d309af),
   Order(e4042351adbd4bb4a93c0f0a66ca56a9), Order(edae448a6299469289b573d07367cc1b)]
   """
   ```

4. Orders made on the 25th of December 2022 with two or more line items.
   What is a "line item"? I think what is requested is that the order should
   contain at least two different types of products. This can be filtered out
   by counting the number of product ids of the order items for an order.

   ```python
   from sqlalchemy import select, func, and_
   from db import Session
   from models import Order, OrderItem
   from datetime import datetime, timedelta

   session = Session()

   order_date = datetime(2022, 12, 25)

   q = (select(Order)
        .where(and_(Order.timestamp >= order_date, Order.timestamp < order_date + timedelta(days=1)))
        .join(Order.order_items)
        .group_by(Order)
        .having(func.count(OrderItem.product_id) >= 2))

   session.scalars(q).all()

   """
   [Order(5159016ade8540f0afdddbb962b73fde), Order(52cfa054a296431789eb25e6e114d592),
   Order(e8c7a680500948179cf4a0982f36270d), Order(fd9a765e9d2843108df21a88602875bc)]
   """
   ```

5. Customers with their first and last order date and time. Hint: the min() and
   max() functions can help with this query.
   Customers have Orders and Orders have timestamps. Try to select all Customer
   and join with Order. Select the min and the max timetamp amongst the orders,
   note that these can be the same if there is only one order made.
   The Orders needs to be grouped by Customer so that the result returns one
   entry per customer and not aggregates the min and max of all orders for all
   customers.

   ```python
   from sqlalchemy import select, func
   from db import Session
   from models import Customer, Order

   first_order_date = func.min(Order.timestamp).label(None)
   latest_order_date = func.max(Order.timestamp).label(None)

   session = Session()

   q = (select(Customer, first_order_date, latest_order_date)
        .join(Customer.orders)
        .group_by(Customer))

   session.execute(q).all()

   """
    [(Customer(000552c55d7b4f21ac76ac221e7e0416), "Wendy Chavez", datetime.datetime(2022, 9, 25, 9, 18, 57), datetime.datetime(2022, 11, 8, 16, 39, 8)),
    (Customer(00150374ff4a43019c99ca59bae7eb84), "Jenna Avery", datetime.datetime(2022, 11, 11, 10, 11, 33), datetime.datetime(2022, 11, 11, 10, 11, 33)),
    (Customer(001c76ec999e48dca40e1fc237617237), "Christopher Jennings", datetime.datetime(2022, 8, 4, 20, 23, 17), datetime.datetime(2022, 8, 27, 3, 57, 57))
    ...]
   """
   ```

6. Select all manufacturers and the sum of all order items that includes their
   product. The result must be sorted by the sum in descending order and grouped
   by the manufacturer.

   ```python
   from sqlalchemy import select, func
   from db import Session
   from models import Manufacturer, Product, OrderItem

   session = Session()

   order_total = func.sum(OrderItem.quantity * OrderItem.unit_price).label(None)
   q = (select(Manufacturer, order_total)
        .join(Manufacturer.products)
        .join(Product.order_items)
        .group_by(Manufacturer)
        .order_by(order_total.desc())
        .limit(5))

   session.execute(q).all()

   """
   [(Manufacturer(14, "Commodore"), 281666.66), (Manufacturer(63, "Sinclair Research"), 122582.62),
   (Manufacturer(5, "Apple Computer"), 34169.33), (Manufacturer(1, "Acorn Computers Ltd"), 14018.279999999999),
   (Manufacturer(8, "Atari, Inc."), 3154.74)]
   """
   ```

7. Select Products and join on column reviews. Group by product, count the
   number of reviews and avg their rating. Order by the review count in
   descending order.

   ```python
   from sqlalchemy import select, func
   from db import Session
   from models import Product, ProductReview

   session = Session()

   review_count = func.count(ProductReview.product_id).label(None)
   product_rating = func.avg(ProductReview.rating).label(None)
 
   q = (select(Product, product_rating, review_count)
        .join(Product.reviews)
        .group_by(Product)
        .order_by(review_count.desc()))

   session.execute(q).all()

   """
   [(Product(41, "Commodore 64"), 3.7563805104408354, 431),
   (Product(48, "Amiga"), 3.7493112947658402, 363),
   (Product(127, "ZX Spectrum"), 4.0, 233)
   ...
   (Product(76, "IBM PS/1"), 4.0, 1), (Product(79, "Hobbit"), 5.0, 1)]
   """
   ```

8. Join products and review table, filter on reviews where the comment is not None,
   use func.avg to calculate the average rating.

   ```python
   from sqlalchemy import select, func
   from db import Session
   from models import Product, ProductReview

   session = Session()

   avg_rating = func.avg(ProductReview.rating).label(None)

   q = (select(Product, avg_rating)
        .join(Product.reviews)
        .where(ProductReview.comment is not None)
        .group_by(Product))

   session.execute(q).all()

   """
   [(Product(74, "Honeywell 316"), 4.0), (Product(16, "Apple II"), 3.633093525179856),
   ...
   Product(33, "Falcon"), 2.5), (Product(6, "A7000"), 3.0)]
   """
   ```

9. Average star rating for the Commodore 64 computer in each month of 2022.
   Here the month and the year must be extracted from the ProductReview 
   timestamp. This can be done using the func.extract function.

   ```python
   from sqlalchemy import select, func
   from db import Session
   from models import Product, ProductReview

   session = Session()

   year = func.extract("year", ProductReview.timestamp).label(None)
   month = func.extract("month", ProductReview.timestamp).label(None)
   rating_avg = func.avg(ProductReview.rating).label(None)

   q = (select(month, rating_avg)
        .join(ProductReview.product)
        .where(Product.name == "Commodore 64")
        .group_by(month)
        .having(year == 2022))

   session.execute(q).all()

   """
   [(1, 4.294117647058823), (2, 3.6551724137931036), (3, 3.4375),
   ...
   (10, 3.9375), (11, 3.8958333333333335), (12, 3.6)]
   """
   ```
