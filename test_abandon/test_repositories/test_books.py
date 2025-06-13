import pytest
from sqlalchemy.orm import Session

from src.models.books import Book
from src.models.categories import Category
from src.repositories.books import BookRepository
from src.repositories.categories import CategoryRepository


def test_create_book(db_session: Session):
    """
    Teste la création d'un livre.
    """
    repository = BookRepository(Book, db_session)
    
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890123",
        "publication_year": 2020,
        "quantity": 5
    }
    
    book = repository.create(obj_in=book_data)
    
    assert book.id is not None
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.isbn == "1234567890123"
    assert book.publication_year == 2020
    assert book.quantity == 5


def test_get_book_by_isbn(db_session: Session):
    """
    Teste la récupération d'un livre par ISBN.
    """
    repository = BookRepository(Book, db_session)
    
    book_data = {
        "title": "ISBN Test Book",
        "author": "ISBN Test Author",
        "isbn": "9876543210123",
        "publication_year": 2021,
        "quantity": 3
    }
    
    repository.create(obj_in=book_data)
    
    book = repository.get_by_isbn(isbn="9876543210123")
    
    assert book is not None
    assert book.title == "ISBN Test Book"
    assert book.isbn == "9876543210123"


def test_search_books(db_session: Session):
    """
    Teste la recherche de livres.
    """
    repository = BookRepository(Book, db_session)
    
    # Créer plusieurs livres
    books_data = [
        {
            "title": "Python Programming",
            "author": "John Doe",
            "isbn": "1111111111111",
            "publication_year": 2019,
            "quantity": 2
        },
        {
            "title": "Advanced Python",
            "author": "Jane Smith",
            "isbn": "2222222222222",
            "publication_year": 2020,
            "quantity": 1
        },
        {
            "title": "Java Programming",
            "author": "Bob Johnson",
            "isbn": "3333333333333",
            "publication_year": 2018,
            "quantity": 3
        }
    ]
    
    for book_data in books_data:
        repository.create(obj_in=book_data)
    
    # Rechercher par titre
    python_books = repository.search(query="Python")
    assert len(python_books) == 2
    
    # Rechercher par auteur
    smith_books = repository.search(query="Smith")
    assert len(smith_books) == 1
    assert smith_books[0].author == "Jane Smith"
    
    # Rechercher par ISBN
    isbn_books = repository.search(query="2222222222222")
    assert len(isbn_books) == 1
    assert isbn_books[0].isbn == "2222222222222"


def test_book_categories(db_session: Session):
    """
    Teste les relations entre livres et catégories.
    """
    book_repository = BookRepository(Book, db_session)
    category_repository = CategoryRepository(Category, db_session)
    
    # Créer des catégories
    programming = category_repository.create(obj_in={"name": "Programming", "description": "Programming books"})
    python = category_repository.create(obj_in={"name": "Python", "description": "Python books"})
    
    # Créer un livre
    book_data = {
        "title": "Python Cookbook",
        "author": "David Beazley",
        "isbn": "4444444444444",
        "publication_year": 2013,
        "quantity": 2
    }
    
    book = book_repository.create(obj_in=book_data)
    
    # Ajouter des catégories au livre
    book_repository.add_category(book_id=book.id, category_id=programming.id)
    book_repository.add_category(book_id=book.id, category_id=python.id)
    
    # Récupérer le livre avec ses catégories
    book_with_categories = book_repository.get_with_categories(id=book.id)
    
    assert book_with_categories is not None
    assert len(book_with_categories.categories) == 2
    category_names = [c.name for c in book_with_categories.categories]
    assert "Programming" in category_names
    assert "Python" in category_names
    
    # Supprimer une catégorie
    book_repository.remove_category(book_id=book.id, category_id=programming.id)
    
    # Vérifier que la catégorie a été supprimée
    book_with_categories = book_repository.get_with_categories(id=book.id)
    assert len(book_with_categories.categories) == 1
    assert book_with_categories.categories[0].name == "Python"