from sqlalchemy import Column, Integer, String, Text

from app.db.session import Base


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    sender = Column(String(100), nullable=True)
    body = Column(Text, nullable=True)
