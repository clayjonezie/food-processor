from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    content = Column(String(255))
    at = Column(DateTime)

    def __init__(self, content=None, at=None):
        self.content = content
        self.at = at

    def __repr__(self):
        return '<Entry: %r>' % self.content
    
