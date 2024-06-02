import uuid
from datetime import datetime

from db.postgres import Base
from sqlalchemy import ARRAY, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.orm import relationship


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    film_id = Column(UUID(as_uuid=True), nullable=False)
    creator_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)
    users = Column(ARRAY(UUID(as_uuid=True)))
    is_active_room = Column(Boolean, default=True)  # Добавлено поле активности
    messages = relationship('Message', back_populates='room')
    player = relationship('Player', back_populates='room')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    room_id = Column(UUID(as_uuid=True),
                     ForeignKey('rooms.id', ondelete='CASCADE'),
                     nullable=False)
    message = Column(TEXT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)  # Добавлено поле created_at
    room = relationship('Room', back_populates='messages')


class Player(Base):
    __tablename__ = 'players'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_active = Column(Boolean, default=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey('rooms.id'))
    view_progress = Column(Integer, nullable=False)
    room = relationship('Room', back_populates='player')


async def save_message_to_db(session, user_id, room_id, message, created_at):
    new_message = Message(
        user_id=user_id,
        room_id=room_id,
        message=message,
        created_at=created_at
    )
    session.add(new_message)
    await session.commit()


async def save_player_to_db(session, is_active, view_progress):
    new_player = Player(
        is_active=is_active,
        view_progress=view_progress
    )
    session.add(new_player)
    await session.commit()
