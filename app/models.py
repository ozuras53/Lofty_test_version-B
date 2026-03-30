from datetime import datetime
from typing import Optional

from pydantic.v1 import BaseModel, HttpUrl
from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    link: Mapped[str] = mapped_column(String(1024), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "link",
            "content_hash",
            name="uq_posts_link_content_hash",
        ),
    )


class PostIn(BaseModel):
    title: str
    link: HttpUrl
    published_at: datetime
    content_hash: str


class PostOut(PostIn):
    id: Optional[int]

