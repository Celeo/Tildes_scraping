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
    score = Column(Integer)

    tags = relationship('Tag', back_populates='topic')
    comments = relationship('Comment', back_populates='topic')

    def to_dict(self):
        return {
            'id': self.id,
            'tildes_id': self.tildes_id,
            'group': self.group,
            'title': self.title,
            'link': self.link,
            'content': self.content,
            'comments_link': self.comments_link,
            'author': self.author,
            'submitted': self.submitted,
            'score': self.score,
            'tags': [tag.name for tag in self.tags]
        }


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    name = Column(String)

    topic = relationship('Topic', back_populates='tags')

    def to_dict(self):
        return {
            'name': self.name
        }


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    tildes_id = Column(String)
    author = Column(String)
    submitted = Column(DateTime)
    content = Column(String)
    score = Column(Integer)

    topic = relationship('Topic', back_populates='comments')

    def to_dict(self):
        return {
            'id': self.id,
            'tildes_id': self.tildes_id,
            'author': self.author,
            'submitted': self.submitted,
            'content': self.content,
            'score': self.score
        }


Session = sessionmaker(bind=engine)


def make_tables() -> None:
    """Creates all the DB tables."""
    Base.metadata.create_all(engine)


def create_session() -> SessionType:
    """Create a new database session."""
    return Session()
