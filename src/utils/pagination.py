from typing import Generic, TypeVar, List, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Query
from fastapi import Query as QueryParam

T = TypeVar('T')


class PaginationParams:
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_desc: bool = False
    ):
        self.skip = skip
        self.limit = limit
        self.sort_by = sort_by
        self.sort_desc = sort_desc


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        arbitrary_types_allowed = True


def paginate(query: Query, params: PaginationParams, schema) -> Page:
    """
    Pagine une requête SQLAlchemy.
    """
    # Compter le nombre total d'éléments
    total = query.count()
    
    # Appliquer le tri si spécifié
    if params.sort_by:
        if hasattr(schema, params.sort_by):
            column = getattr(schema, params.sort_by)
            if params.sort_desc:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)
    
    # Appliquer la pagination
    items = query.offset(params.skip).limit(params.limit).all()
    
    # Calculer le nombre de pages
    pages = (total + params.limit - 1) // params.limit if params.limit > 0 else 1
    page = (params.skip // params.limit) + 1 if params.limit > 0 else 1
    
    return Page(
        items=items,
        total=total,
        page=page,
        size=params.limit,
        pages=pages
    )