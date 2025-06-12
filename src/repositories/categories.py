from sqlalchemy.orm import Session
from typing import List, Optional

from .base import BaseRepository
from ..models.categories import Category


class CategoryRepository(BaseRepository[Category, None, None]):
    def get_by_name(self, *, name: str) -> Optional[Category]:
        """
        Récupère une catégorie par son nom.
        """
        return self.db.query(Category).filter(Category.name == name).first()
    
    def get_or_create(self, *, name: str, description: Optional[str] = None) -> Category:
        """
        Récupère une catégorie par son nom ou la crée si elle n'existe pas.
        """
        category = self.get_by_name(name=name)
        if not category:
            category_data = {"name": name}
            if description:
                category_data["description"] = description
            category = self.create(obj_in=category_data)
        return category