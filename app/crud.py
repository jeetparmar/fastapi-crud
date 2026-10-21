from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, schemas
from .security import hash_password


# ---- users ----
def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.scalar(select(models.User).where(models.User.email == email.lower()))


def create_user(db: Session, data: schemas.UserCreate) -> models.User:
    user = models.User(email=data.email.lower(), hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    return user


# ---- items (always scoped to the owner) ----
def list_items(
    db: Session, owner_id: int, *, q: str | None, in_stock: bool | None, limit: int, offset: int
) -> tuple[list[models.Item], int]:
    stmt = select(models.Item).where(models.Item.owner_id == owner_id)
    if q:
        stmt = stmt.where(models.Item.name.ilike(f"%{q}%"))
    if in_stock is not None:
        stmt = stmt.where(models.Item.in_stock == in_stock)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(models.Item.id).limit(limit).offset(offset)).all()
    return list(rows), total


def get_item(db: Session, owner_id: int, item_id: int) -> models.Item | None:
    item = db.get(models.Item, item_id)
    return item if item and item.owner_id == owner_id else None


def create_item(db: Session, owner_id: int, data: schemas.ItemCreate) -> models.Item:
    item = models.Item(**data.model_dump(), owner_id=owner_id)
    db.add(item)
    db.commit()
    return item


def update_item(db: Session, item: models.Item, data: schemas.ItemUpdate) -> models.Item:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    return item


def delete_item(db: Session, item: models.Item) -> None:
    db.delete(item)
    db.commit()
