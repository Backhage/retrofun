# The fifth set of exercises are listed below

Solutions are my own and there might be better ways to solve it them.

## Exercises

Write queries that return:

1. Blog posts that have received more than 40 page views in March 2020.

2. Blog article with the largest number of translations. In case of a tie,
   the article that comes first alphabetically should be returned.

3. Page views in March 2022, categorized by language.

4. Page views by article, only considering content in German.

5. Monthly page views between January and December 2022.

6. Daily page views in February 2022.

## Solutions

Here are the current models for reference.

```python
ProductCountry = Table(
    "products_countries",
    Model.metadata,
    Column("product_id", ForeignKey("products.id"),
           primary_key=True, nullable=False),
    Column("country_id", ForeignKey("countries.id"),
           primary_key=True, nullable=False),
)
```

```python
class Product(Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id"), index=True
    )
    manufacturer: Mapped["Manufacturer"] = relationship(
        back_populates="products")
    year: Mapped[int] = mapped_column(index=True)

    countries: Mapped[list["Country"]] = relationship(
        secondary=ProductCountry, back_populates="products"
    )
    cpu: Mapped[Optional[str]] = mapped_column(String(32))

    order_items: WriteOnlyMapped["OrderItem"] = relationship(
        back_populates="product")

    reviews: WriteOnlyMapped["ProductReview"] = relationship(
        back_populates="product")

    blog_articles: WriteOnlyMapped["BlogArticle"] = relationship(
        back_populates="product"
    )

    def __repr__(self):
        return f'Product({self.id}, "{self.name}")'
```

```python
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

```python
class Country(Model):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True, unique=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=ProductCountry, back_populates="countries"
    )

    def __repr__(self):
        return f'Country({self.id}, "{self.name}")'
```

```python
class Order(Model):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id"), index=True)
    customer: Mapped["Customer"] = relationship(back_populates="orders")

    order_items: Mapped[list["OrderItem"]
                        ] = relationship(back_populates="order")

    def __repr__(self):
        return f"Order({self.id.hex})"
```

```python
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

    blog_users: WriteOnlyMapped["BlogUser"] = relationship(
        back_populates="customer")

    def __repr__(self):
        return f'Customer({self.id.hex}), "{self.name}"'
```

```python
class OrderItem(Model):
    __tablename__ = "orders_items"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), primary_key=True)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id"), primary_key=True)

    product: Mapped["Product"] = relationship(back_populates="order_items")
    order: Mapped["Order"] = relationship(back_populates="order_items")

    unit_price: Mapped[float]
    quantity: Mapped[int]
```

```python
class ProductReview(Model):
    __tablename__ = "product_reviews"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id"), primary_key=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )
    rating: Mapped[int]
    comment: Mapped[str | None] = mapped_column(Text)

    product: Mapped["Product"] = relationship(back_populates="reviews")
    customer: Mapped["Customer"] = relationship(
        back_populates="product_reviews")
```

```python
class BlogArticle(Model):
    __tablename__ = "blog_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    translation_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("blog_articles.id"), index=True)
    translation_of: Mapped[Optional["BlogArticle"]] = relationship(
        remote_side=id, back_populates="translations")
    translations: Mapped[list["BlogArticle"]] = relationship(
        back_populates="translation_of")
    title: Mapped[str] = mapped_column(String(128), index=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("blog_authors.id"), index=True)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id"), index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )
    author: Mapped["BlogAuthor"] = relationship(back_populates="articles")
    product: Mapped[Optional["Product"]] = relationship(
        back_populates="blog_articles")

    views: WriteOnlyMapped["BlogView"] = relationship(back_populates="article")

    language_id: Mapped[int | None] = mapped_column(
        ForeignKey("languages.id"), index=True)

    language: Mapped[Optional["Language"]] = relationship(
        back_populates="blog_articles")

    def __repr__(self):
        return f'BlogArticle({self.id}, "{self.title}")'
```

```python
class BlogAuthor(Model):
    __tablename__ = "blog_authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    articles: WriteOnlyMapped["BlogArticle"] = relationship(
        back_populates="author")

    def __repr__(self):
        return f'BlogAuthor({self.id}, "{self.name}")'
```

```python
class BlogUser(Model):
    __tablename__ = "blog_users"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    customer_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("customers.id"), index=True)

    customer: Mapped[Optional["Customer"]] = relationship(
        back_populates="blog_users")
    sessions: WriteOnlyMapped["BlogSession"] = relationship(
        back_populates="user")

    def __repr__(self):
        return f"BlogUser({self.id.hex})"
```

```python
class BlogSession(Model):
    __tablename__ = "blog_sessions"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("blog_users.id"), index=True)
    user: Mapped["BlogUser"] = relationship(back_populates="sessions")

    views: WriteOnlyMapped["BlogView"] = relationship(back_populates="session")

    def __repr__(self):
        return f"BlogSession({self.id.hex})"
```

```python
class BlogView(Model):
    __tablename__ = "blog_views"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("blog_articles.id"))
    sesion_id: Mapped[UUID] = mapped_column(ForeignKey("blog_sessions.id"))
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True)

    article: Mapped["BlogArticle"] = relationship(back_populates="views")
    session: Mapped["BlogSession"] = relationship(back_populates="views")
```

```python
class Language(Model):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True, unique=True)

    blog_articles: WriteOnlyMapped["BlogArticle"] = relationship(
        back_populates="language")

    def __repr__(self):
        return f'Language({self.id}, "{self.name}")'
```

1. Blog posts that have received more than 40 page views in March 2020.

    ```python
    from datetime import datetime
    from sqlalchemy import select, func
    from db import session
    from models import blogarticle, blogview

    view_count = func.count(blogview.id).label(none)

    session = session()

    q = (select(blogarticle, view_count)
        .join(blogarticle.views)
        .where(blogview.timestamp.between(datetime(2020, 3, 1), datetime(2020, 4, 1)))
        .group_by(blogarticle)
        .having(view_count > 40)
        .order_by(view_count.desc()))

    session.execute(q).all()

    """
    [(blogarticle(143, "evening however issue"), 52),
    (blogarticle(75, "these data raise support interview"), 46),
    (blogarticle(183, "man southern senior soon"), 44),
    (blogarticle(150, "court event citizen see feel side picture"), 43),
    (blogarticle(176, "on amount with building"), 43),
    (blogarticle(172, "artist cultural above director country contain happen"), 42),
    (blogarticle(181, "relate material election"), 42)]
    """
    ```

2. Blog article with the largest number of translations. In case of a tie,
   the article that comes first alphabetically should be returned.

    ```python
    from sqlalchemy import select, func, aliased
    from sqlalchemy.orm import aliased
    from db import Session
    from models import BlogArticle

    translations = func.count(BlogArticle.id).label(None)
    TranslatedBlogArticle = aliased(BlogArticle)

    session = Session()

    q = (select(BlogArticle, translations)
        .join(TranslatedBlogArticle.translation_of)
        .group_by(BlogArticle)
        .order_by(translations.desc(), BlogArticle.title)
        .limit(1))

    session.execute(q).all()

    """
    [(BlogArticle(63, "Business seven ability cup church similar itself"), 3)]
    """
    ```
