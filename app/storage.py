from datetime import datetime
from typing import Iterable, List

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from .config import settings
from .models import Base, Post, PostIn, PostOut


class Storage:
    """
    Слой хранения постов и логика дедупликации.
    """

    def __init__(self) -> None:
        self.engine = create_engine(settings.database_url, echo=False, future=True)
        Base.metadata.create_all(self.engine)

    def save_new_posts(self, posts: Iterable[PostIn]) -> List[PostOut]:
        """
        Сохранить только те посты, которых ещё нет в базе (дедупликация по link + content_hash).

        Возвращает список реально добавленных постов.
        """
        saved_posts: List[PostOut] = []
        with Session(self.engine) as session:
            for post_in in posts:
                if self._is_post_new(session, post_in):
                    db_post = Post(
                        title=post_in.title,
                        link=str(post_in.link),
                        published_at=post_in.published_at,
                        content_hash=post_in.content_hash,
                        created_at=datetime.utcnow(),
                    )
                    session.add(db_post)
                    session.flush()
                    saved_posts.append(
                        PostOut(
                            id=db_post.id,
                            title=db_post.title,
                            link=db_post.link,
                            published_at=db_post.published_at,
                            content_hash=db_post.content_hash,
                        )
                    )
            session.commit()
        print(f"[Storage] Сохранено новых постов: {len(saved_posts)}")
        return saved_posts

    @staticmethod
    def _is_post_new(session: Session, post_in: PostIn) -> bool:
        """
        Проверить, существует ли уже пост с теми же link и content_hash.
        """
        stmt = select(Post).where(
            Post.link == str(post_in.link),
            Post.content_hash == post_in.content_hash,
        )
        exists = session.execute(stmt).scalar_one_or_none()
        return exists is None

