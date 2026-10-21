from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from .. import crud, schemas
from ..deps import DB, CurrentUser

router = APIRouter(prefix="/items", tags=["items"])


def _get_or_404(db, user, item_id: int):
    item = crud.get_item(db, user.id, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    return item


@router.post("", response_model=schemas.ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: schemas.ItemCreate, db: DB, user: CurrentUser):
    return crud.create_item(db, user.id, payload)


@router.get("", response_model=schemas.Page)
def list_items(
    db: DB,
    user: CurrentUser,
    q: Annotated[str | None, Query(description="Search by name")] = None,
    in_stock: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    items, total = crud.list_items(db, user.id, q=q, in_stock=in_stock, limit=limit, offset=offset)
    return schemas.Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(item_id: int, db: DB, user: CurrentUser):
    return _get_or_404(db, user, item_id)


@router.patch("/{item_id}", response_model=schemas.ItemOut)
def update_item(item_id: int, payload: schemas.ItemUpdate, db: DB, user: CurrentUser):
    return crud.update_item(db, _get_or_404(db, user, item_id), payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: DB, user: CurrentUser):
    crud.delete_item(db, _get_or_404(db, user, item_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
