from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import Session as SessionType


engine = create_engine('sqlite:///data.db')
Base = declarative_base()


class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True)
    tildes_id = Column(String)
    group = Column(String)
    title = Column(String)
    link = Column(String)
    content = Column(String)
    comments_link = Column(String)
    author = Column(String)
    submitted = Column(DateTime)

    tags = relationship('Tag', back_populates='topic')
    comments = relationship('Comment', back_populates='topic')


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    name = Column(String)

    topic = relationship('Topic', back_populates='tags')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    tildes_id = Column(String)
    author = Column(String)
    submitted = Column(DateTime)
    content = Column(String)

    topic = relationship('Topic', back_populates='comments')


Session = sessionmaker(bind=engine)


def make_tables() -> None:
    """Creates all the DB tables."""
    Base.metadata.create_all(engine)


def create_session() -> SessionType:
    """Create a new database session."""
    return Session()
