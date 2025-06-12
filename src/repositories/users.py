from sqlalchemy.orm import Session

from .base import BaseRepository
from ..models.users import User


class UserRepository(BaseRepository[User, None, None]):
    def get_by_email(self, *, email: str) -> User:
        """
        Récupère un utilisateur par son email.
        """
        return self.db.query(User).filter(User.email == email).first()