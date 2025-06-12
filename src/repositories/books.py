from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional, Dict, Any

from .base import BaseRepository
from ..models.books import Book
from ..models.categories import Category, book_category
from ..utils.cache import cache, invalidate_cache

class BookRepository(BaseRepository[Book, None, None]):
    def get_by_isbn(self, *, isbn: str) -> Optional[Book]:
        """
        Récupère un livre par son ISBN.
        """
        return self.db.query(Book).filter(Book.isbn == isbn).first()
    
    def get_by_title(self, *, title: str) -> List[Book]:
        """
        Récupère des livres par leur titre (recherche partielle).
        """
        return self.db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()
    
    def get_by_author(self, *, author: str) -> List[Book]:
        """
        Récupère des livres par leur auteur (recherche partielle).
        """
        return self.db.query(Book).filter(Book.author.ilike(f"%{author}%")).all()
    
    def get_with_categories(self, *, id: int) -> Optional[Book]:
        """
        Récupère un livre avec ses catégories.
        """
        return self.db.query(Book).options(joinedload(Book.categories)).filter(Book.id == id).first()
    
    def get_multi_with_categories(self, *, skip: int = 0, limit: int = 100) -> List[Book]:
        """
        Récupère plusieurs livres avec leurs catégories.
        """
        return self.db.query(Book).options(joinedload(Book.categories)).offset(skip).limit(limit).all()
    
    def search(self, *, query: str) -> List[Book]:
        """
        Recherche des livres par titre, auteur ou ISBN.
        """
        return self.db.query(Book).filter(
            or_(
                Book.title.ilike(f"%{query}%"),
                Book.author.ilike(f"%{query}%"),
                Book.isbn.ilike(f"%{query}%")
            )
        ).all()
    
    def get_by_category(self, *, category_id: int, skip: int = 0, limit: int = 100) -> List[Book]:
        """
        Récupère des livres par catégorie.
        """
        return self.db.query(Book).join(book_category).filter(
            book_category.c.category_id == category_id
        ).offset(skip).limit(limit).all()
    
    def add_category(self, *, book_id: int, category_id: int) -> None:
        """
        Ajoute une catégorie à un livre.
        """
        book = self.get(id=book_id)
        if not book:
            raise ValueError(f"Livre avec l'ID {book_id} non trouvé")
        
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise ValueError(f"Catégorie avec l'ID {category_id} non trouvée")
        
        book.categories.append(category)
        self.db.commit()
    
    def remove_category(self, *, book_id: int, category_id: int) -> None:
        """
        Supprime une catégorie d'un livre.
        """
        book = self.get(id=book_id)
        if not book:
            raise ValueError(f"Livre avec l'ID {book_id} non trouvé")
        
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise ValueError(f"Catégorie avec l'ID {category_id} non trouvée")
        
        book.categories.remove(category)
        self.db.commit()
    
    @cache(expiry=60)  # Cache pendant 1 minute
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur les livres.
        """
        total_books = self.db.query(func.sum(Book.quantity)).scalar() or 0
        unique_books = self.db.query(func.count(Book.id)).scalar() or 0
        avg_publication_year = self.db.query(func.avg(Book.publication_year)).scalar() or 0
        
        return {
            "total_books": total_books,
            "unique_books": unique_books,
            "avg_publication_year": avg_publication_year
        }
    def create(self, *, obj_in: Any) -> Book:
        """
        Crée un nouveau livre et invalide le cache.
        """
        book = super().create(obj_in=obj_in)
        invalidate_cache("src.repositories.books")
        return book
    
    def update(self, *, db_obj: Book, obj_in: Any) -> Book:
        """
        Met à jour un livre et invalide le cache.
        """
        book = super().update(db_obj=db_obj, obj_in=obj_in)
        invalidate_cache("src.repositories.books")
        return book
    
    def remove(self, *, id: int) -> Book:
        """
        Supprime un livre et invalide le cache.
        """
        book = super().remove(id=id)
        invalidate_cache("src.repositories.books")
        return book