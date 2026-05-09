from typing import Any, Generic, List, Optional, Type, TypeVar, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        return self.db.get(self.model, id)

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def create(self, *, obj_in: Any) -> ModelType:
        # Note: obj_in can be a dict or a Pydantic model
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.flush()
        # Commit and refresh are removed here to allow for transactional integrity at the service level
        return db_obj

    def update(self, *, db_obj: ModelType, obj_in: Any) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        self.db.add(db_obj)
        return db_obj

    def remove(self, *, id: Any) -> Optional[ModelType]:
        obj = self.db.get(self.model, id)
        if obj:
            self.db.delete(obj)
        return obj
