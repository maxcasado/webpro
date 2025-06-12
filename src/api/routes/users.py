from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from ...db.session import get_db
from ...models.users import User as UserModel
from ..schemas.users import User, UserCreate, UserUpdate
from ...repositories.users import UserRepository
from ...services.users import UserService
from ..dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100 #,
    #current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère la liste des utilisateurs.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    users = service.get_multi(skip=skip, limit=limit)
    return users


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
    #,
    #current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Crée un nouvel utilisateur.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    
    
    try:
        
        user = service.create(obj_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=User)
def read_user_me(
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Récupère l'utilisateur connecté.
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Met à jour l'utilisateur connecté.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    
    try:
        user = service.update(db_obj=current_user, obj_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{id}", response_model=User)
def read_user(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère un utilisateur par son ID.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get(id=id)
    if not user:
        raise HTTPException( 
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return user


@router.put("/{id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    id: int,
    user_in: UserUpdate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Met à jour un utilisateur.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get(id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    try:
        user = service.update(db_obj=user, obj_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Supprime un utilisateur.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get(id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Empêcher la suppression de l'utilisateur connecté
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer l'utilisateur connecté"
        )
    
    user = service.remove(id=id)
    return user


@router.get("/by-email/{email}", response_model=User)
def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère un utilisateur par son email.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get_by_email(email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return user
