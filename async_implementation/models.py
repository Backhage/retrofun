from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from db import Model

ProductCountry = Table(
    "products_countries",
    Model.metadata,
    Column("product_id", ForeignKey("products.id"),
           primary_key=True, nullable=False),
    Column("country_id", ForeignKey("countries.id"),
           primary_key=True, nullable=False),
)


class Product(Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id"), index=True
    )
    manufacturer: Mapped["Manufacturer"] = relationship(
        lazy="joined", innerjoin=True, back_populates="products"
    )
    year: Mapped[int] = mapped_column(index=True)

    countries: Mapped[list["Country"]] = relationship(
        lazy="selectin", secondary=ProductCountry, back_populates="products"
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


class Manufacturer(Model):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    products: Mapped[list["Product"]] = relationship(
        lazy="selectin", back_populates="manufacturer", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'Manufacturer({self.id}, "{self.name}")'


class Country(Model):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True, unique=True)

    products: Mapped[list["Product"]] = relationship(
        lazy="selectin", secondary=ProductCountry, back_populates="countries"
    )

    def __repr__(self):
        return f'Country({self.id}, "{self.name}")'


class Order(Model):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id"), index=True)
    customer: Mapped["Customer"] = relationship(
        lazy="joined", innerjoin=True, back_populates="orders"
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        lazy="selectin", back_populates="order"
    )

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

    blog_users: WriteOnlyMapped["BlogUser"] = relationship(
        back_populates="customer")

    def __repr__(self):
        return f'Customer({self.id.hex}), "{self.name}"'


class OrderItem(Model):
    """This is a join table for the many-to-many relationship between orders
    and products. It differs from the join table defined earlier for the
    products to countries table in that this has additional columns for extra
    data that is part of the join table itself. This alternative method to
    define a many-to-many relationship is called the Association Object
    Pattern.
    """

    __tablename__ = "orders_items"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), primary_key=True)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id"), primary_key=True)

    product: Mapped["Product"] = relationship(
        lazy="joined", innerjoin=True, back_populates="order_items"
    )
    order: Mapped["Order"] = relationship(
        lazy="joined", innerjoin=True, back_populates="order_items"
    )

    unit_price: Mapped[float]
    quantity: Mapped[int]


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

    product: Mapped["Product"] = relationship(
        lazy="joined", innerjoin=True, back_populates="reviews"
    )
    customer: Mapped["Customer"] = relationship(
        lazy="joined", innerjoin=True, back_populates="product_reviews"
    )


class BlogArticle(Model):
    __tablename__ = "blog_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    translation_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("blog_articles.id"), index=True
    )
    translation_of: Mapped[Optional["BlogArticle"]] = relationship(
        lazy="joined", remote_side=id, back_populates="translations"
    )
    translations: Mapped[list["BlogArticle"]] = relationship(
        lazy="selectin", back_populates="translation_of"
    )
    title: Mapped[str] = mapped_column(String(128), index=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("blog_authors.id"), index=True)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id"), index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )
    author: Mapped["BlogAuthor"] = relationship(
        lazy="joined", innerjoin=True, back_populates="articles"
    )
    product: Mapped[Optional["Product"]] = relationship(
        lazy="joined", back_populates="blog_articles"
    )

    views: WriteOnlyMapped["BlogView"] = relationship(back_populates="article")

    language_id: Mapped[int | None] = mapped_column(
        ForeignKey("languages.id"), index=True
    )

    language: Mapped[Optional["Language"]] = relationship(
        lazy="joined", back_populates="blog_articles"
    )

    def __repr__(self):
        return f'BlogArticle({self.id}, "{self.title}")'


class BlogAuthor(Model):
    __tablename__ = "blog_authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    articles: WriteOnlyMapped["BlogArticle"] = relationship(
        back_populates="author")

    def __repr__(self):
        return f'BlogAuthor({self.id}, "{self.name}")'


class BlogUser(Model):
    __tablename__ = "blog_users"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    customer_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("customers.id"), index=True
    )

    customer: Mapped[Optional["Customer"]] = relationship(
        lazy="joined", back_populates="blog_users"
    )
    sessions: WriteOnlyMapped["BlogSession"] = relationship(
        back_populates="user")

    def __repr__(self):
        return f"BlogUser({self.id.hex})"


class BlogSession(Model):
    __tablename__ = "blog_sessions"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("blog_users.id"), index=True)
    user: Mapped["BlogUser"] = relationship(
        lazy="joined", innerjoin=True, back_populates="sessions"
    )

    views: WriteOnlyMapped["BlogView"] = relationship(back_populates="session")

    def __repr__(self):
        return f"BlogSession({self.id.hex})"


class BlogView(Model):
    __tablename__ = "blog_views"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("blog_articles.id"))
    sesion_id: Mapped[UUID] = mapped_column(ForeignKey("blog_sessions.id"))
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )

    article: Mapped["BlogArticle"] = relationship(
        lazy="joined", innerjoin=True, back_populates="views"
    )
    session: Mapped["BlogSession"] = relationship(
        lazy="joined", innerjoin=True, back_populates="views"
    )


class Language(Model):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True, unique=True)

    blog_articles: WriteOnlyMapped["BlogArticle"] = relationship(
        back_populates="language"
    )

    def __repr__(self):
        return f'Language({self.id}, "{self.name}")'
