from app.db.base import Base
from app.db.session import engine
from app.models import paper, paper_analysis
from sqlalchemy import inspect, text


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    add_missing_content_column()


def add_missing_content_column() -> None:
    inspector = inspect(engine)
    if "papers" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("papers")}
    if "content" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE papers ADD COLUMN content TEXT"))
