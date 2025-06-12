from typing import Optional, List, Any, Dict, Union
from sqlalchemy.orm import Session

from ..repositories.users import UserRepository
from ..models.users import User
from ..api.schemas.users import UserCreate, UserUpdate
from ..utils.security import get_password_hash, verify_password
from .base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """
    Service pour la gestion des utilisateurs.
    """
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repository = repository
    
    def get_by_email(self, *, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email.
        """
        return self.repository.get_by_email(email=email)
    
    def create(self, *, obj_in: UserCreate) -> User:
        """
        Crée un nouvel utilisateur avec un mot de passe hashé.
        """
        # Vérifier si l'email est déjà utilisé
        existing_user = self.get_by_email(email=obj_in.email)
        if existing_user:
            raise ValueError("L'email est déjà utilisé")
        
        # Hasher le mot de passe
        hashed_password = get_password_hash(obj_in.password)
        user_data = obj_in.dict()
        del user_data["password"]
        user_data["hashed_password"] = hashed_password
        
        return self.repository.create(obj_in=user_data)
    
    def update(
        self,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Met à jour un utilisateur, en hashant le nouveau mot de passe si fourni.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]
        
        return super().update(db_obj=db_obj, obj_in=update_data)
    
    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur par email et mot de passe.
        """
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, *, user: User) -> bool:
        """
        Vérifie si un utilisateur est actif.
        """
        return user.is_active
    
    def is_admin(self, *, user: User) -> bool:
        """
        Vérifie si un utilisateur est administrateur.
        """
        return user.is_admin