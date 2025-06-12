from sqlalchemy import Column, Integer, String, Text, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base
from .categories import book_category  # Importez la table d'association


class Book(Base):
    title = Column(String(100), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    isbn = Column(String(13), nullable=False, unique=True, index=True)
    publication_year = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    publisher = Column(String(100), nullable=True)
    language = Column(String(50), nullable=True)
    pages = Column(Integer, nullable=True)
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('publication_year >= 1000 AND publication_year <= %d' % datetime.now().year, name='check_publication_year'),
        CheckConstraint('quantity >= 0', name='check_quantity'),
        CheckConstraint('pages > 0', name='check_pages'),
        # Index composite sur titre et auteur pour les recherches
        Index('idx_book_title_author', 'title', 'author'),
    )
    
    # Relations
    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=book_category, back_populates="books")
