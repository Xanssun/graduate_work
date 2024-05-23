from datetime import datetime
from functools import lru_cache
from typing import List, Optional
from uuid import UUID

from db.postgres import get_session
from fastapi import Depends, HTTPException
from models.entity import Room
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class RoomService:
    
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(self, film_id: UUID, creator_id: UUID, users: List[UUID]) -> Room:
        # Проверьте, есть ли у пользователя активная комната
        query = select(Room).filter(Room.creator_id == creator_id, Room.is_active_room == True)
        result = await self.db_session.execute(query)
        active_room = result.scalars().first()
        
        if active_room:
            raise HTTPException(status_code=400, detail="User already has an active room")

        new_room = Room(film_id=film_id,
                        creator_id=creator_id,
                        created_at=datetime.utcnow(),
                        users=users)
        self.db_session.add(new_room)
        await self.db_session.commit()
        return new_room

    async def get(self, room_id: UUID) -> Optional[Room]:
        return await self.db_session.get(Room, room_id)

@lru_cache
def get_room_service(
    db_session: AsyncSession = Depends(get_session),
) -> RoomService:
    return RoomService(db_session=db_session)
