from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from ...db.session import get_db
from ...models.categories import Category as CategoryModel
from ..schemas.books import Category, CategoryCreate, CategoryUpdate
from ...repositories.categories import CategoryRepository
from ..dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=List[Category])
def read_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Récupère la liste des catégories.
    """
    repository = CategoryRepository(CategoryModel, db)
    categories = repository.get_multi(skip=skip, limit=limit)
    return categories


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Crée une nouvelle catégorie.
    """
    repository = CategoryRepository(CategoryModel, db)
    
    # Check if category name already exists
    existing_category = repository.get_by_name(name=category_in.name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une catégorie avec ce nom existe déjà"
        )
    
    category = repository.create(obj_in=category_in)
    return category


@router.get("/{id}", response_model=Category)
def read_category(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Récupère une catégorie par son ID.
    """
    repository = CategoryRepository(CategoryModel, db)
    category = repository.get(id=id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catégorie non trouvée"
        )
    return category


@router.put("/{id}", response_model=Category)
def update_category(
    *,
    db: Session = Depends(get_db),
    id: int,
    category_in: CategoryUpdate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Met à jour une catégorie.
    """
    repository = CategoryRepository(CategoryModel, db)
    category = repository.get(id=id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catégorie non trouvée"
        )
    
    # Check if new name conflicts with existing category (if name is being changed)
    if category_in.name and category_in.name != category.name:
        existing_category = repository.get_by_name(name=category_in.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une catégorie avec ce nom existe déjà"
            )
    
    category = repository.update(db_obj=category, obj_in=category_in)
    return category


@router.delete("/{id}", response_model=Category)
def delete_category(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Supprime une catégorie.
    """
    repository = CategoryRepository(CategoryModel, db)
    category = repository.get(id=id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catégorie non trouvée"
        )
    
    category = repository.remove(id=id)
    return category


@router.get("/name/{name}", response_model=Category)
def get_category_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Récupère une catégorie par son nom.
    """
    repository = CategoryRepository(CategoryModel, db)
    category = repository.get_by_name(name=name)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catégorie non trouvée"
        )
    return category
