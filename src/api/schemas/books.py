from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Nom de la catégorie")
    description: Optional[str] = Field(None, max_length=200, description="Description de la catégorie")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Nom de la catégorie")


class CategoryInDBBase(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Category(CategoryInDBBase):
    pass


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Titre du livre")
    author: str = Field(..., min_length=1, max_length=100, description="Auteur du livre")
    isbn: str = Field(..., min_length=10, max_length=13, description="ISBN du livre")
    publication_year: int = Field(..., ge=1000, le=datetime.now().year, description="Année de publication")
    description: Optional[str] = Field(None, max_length=1000, description="Description du livre")
    quantity: int = Field(..., ge=0, description="Nombre d'exemplaires disponibles")
    publisher: Optional[str] = Field(None, max_length=100, description="Éditeur du livre")
    language: Optional[str] = Field(None, max_length=50, description="Langue du livre")
    pages: Optional[int] = Field(None, gt=0, description="Nombre de pages")


class BookCreate(BookBase):
    category_ids: Optional[List[int]] = Field(None, description="IDs des catégories")


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Titre du livre")
    author: Optional[str] = Field(None, min_length=1, max_length=100, description="Auteur du livre")
    isbn: Optional[str] = Field(None, min_length=10, max_length=13, description="ISBN du livre")
    publication_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year, description="Année de publication")
    description: Optional[str] = Field(None, max_length=1000, description="Description du livre")
    quantity: Optional[int] = Field(None, ge=0, description="Nombre d'exemplaires disponibles")
    publisher: Optional[str] = Field(None, max_length=100, description="Éditeur du livre")
    language: Optional[str] = Field(None, max_length=50, description="Langue du livre")
    pages: Optional[int] = Field(None, gt=0, description="Nombre de pages")
    category_ids: Optional[List[int]] = Field(None, description="IDs des catégories")


class BookInDBBase(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Book(BookInDBBase):
    categories: List[Category] = []