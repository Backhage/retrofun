import csv
from datetime import datetime
from pathlib import Path
from sqlalchemy import select, delete
from db import Session
from models import BlogArticle, BlogAuthor, Product, BlogView, BlogSession, BlogUser


def main():
    with Session() as session:
        with session.begin():
            session.execute(delete(BlogView))
            session.execute(delete(BlogSession))
            session.execute(delete(BlogUser))
            session.execute(delete(BlogArticle))
            session.execute(delete(BlogAuthor))

        with Session() as session:
            with session.begin():
                all_authors = {}
                all_products = {}

                with Path("articles.csv").open() as f:
                    reader = csv.DictReader(f)

                    for row in reader:
                        author = all_authors.get(row["author"])
                        if author is None:
                            author = BlogAuthor(name=row["author"])
                            all_authors[author.name] = author

                        product = None
                        if row["product"]:
                            product = all_products.get(row["product"])
                            if product is None:
                                product = session.scalar(
                                    select(Product).where(
                                        Product.name == row["product"]
                                    )
                                )
                                if product is not None:
                                    all_products[product.name] = product

                        article = BlogArticle(
                            title=row["title"],
                            author=author,
                            product=product,
                            timestamp=datetime.strptime(
                                row["timestamp"], "%Y-%m-%d %H:%M:%S"
                            ),
                        )
                        session.add(article)


if __name__ == "__main__":
    main()
