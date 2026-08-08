from sqlalchemy import Column, Integer, String, Text

from app.db.session import Base


class EmailThread(Base):
    __tablename__ = "email_threads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    subject = Column(String(255), nullable=True)
    body = Column(Text, nullable=True)
