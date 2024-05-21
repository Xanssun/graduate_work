from datetime import datetime
import uuid

from db.postgres import Base
from sqlalchemy import Column, String, Integer, DateTime, ARRAY, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    """Тестовая модель юзер для теста миграций"""
    __tablename__ = "User"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    film_id = Column(UUID(as_uuid=True), nullable=False)
    creator_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = Column(ARRAY(UUID(as_uuid=True)))
    message = relationship('Message', back_populates='room')
    player = relationship('Player', back_populates='room')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    room_id = Column(UUID(as_uuid=True),
                     ForeignKey('rooms.id', ondelete='CASCADE'),
                     nullable=False)
    message = Column(String, nullable=False)
    room = relationship('Room', back_populates='message')


class Player(Base):
    __tablename__ = 'players'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True),
                     ForeignKey('rooms.id', ondelete='CASCADE'),
                     nullable=False)
    is_active = Column(Boolean, default=False)
    view_progress = Column(Integer, nullable=False)
    room = relationship('Room', back_populates='player')
