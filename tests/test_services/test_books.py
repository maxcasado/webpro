import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from src.models.books import Book as BookModel
from src.repositories.books import BookRepository
from src.services.books import BookService
from src.api.schemas.books import BookCreate, BookUpdate


def test_create_book(db_session: Session):
    """
    Test de création d'un livre.
    """
    # Arrange
    repository = BookRepository(BookModel, db_session)
    service = BookService(repository)
    
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890123",
        "publication_year": 2023,
        "description": "Test description",
        "quantity": 5,
        "publisher": "Test Publisher",
        "language": "French",
        "pages": 200
    }
    book_in = BookCreate(**book_data)
    
    # Act
    book = service.create(obj_in=book_in)
    
    # Assert
    assert book.title == book_data["title"]
    assert book.author == book_data["author"]
    assert book.isbn == book_data["isbn"]
    assert book.publication_year == book_data["publication_year"]
    assert book.description == book_data["description"]
    assert book.quantity == book_data["quantity"]
    assert book.publisher == book_data["publisher"]
    assert book.language == book_data["language"]
    assert book.pages == book_data["pages"]
    assert book.id is not None


def test_get_book(db_session: Session):
    """
    Test de récupération d'un livre par son ID.
    """
    # Arrange
    repository = BookRepository(BookModel, db_session)
    service = BookService(repository)
    
    # Créer un livre pour le test
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890123",
        "publication_year": 2023,
        "quantity": 5
    }
    book_model = BookModel(**book_data)
    db_session.add(book_model)
    db_session.commit()
    db_session.refresh(book_model)
    
    # Act
    book = service.get(id=book_model.id)
    
    # Assert
    assert book is not None
    assert book.id == book_model.id
    assert book.title == book_data["title"]
    assert book.author == book_data["author"]


def test_get_nonexistent_book(db_session: Session):
    """
    Test de récupération d'un livre inexistant.
    """
    # Arrange
    repository = BookRepository(BookModel, db_session)
    service = BookService(repository)
    
    # Act
    book = service.get(id=999)
    
    # Assert
    assert book is None


def test_update_book(db_session: Session):
    """
    Test de mise à jour d'un livre.
    """
    # Arrange
    repository = BookRepository(BookModel, db_session)
    service = BookService(repository)
    
    # Créer un livre pour le test
    book_data = {
        "title": "Original Title",
        "author": "Original Author",
        "isbn": "1234567890123",
        "publication_year": 2023,
        "quantity": 5
    }
    book_model = BookModel(**book_data)
    db_session.add(book_model)
    db_session.commit()
    db_session.refresh(book_model)
    
    # Données de mise à jour
    update_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "quantity": 10
    }
    book_update = BookUpdate(**update_data)
    
    # Act
    updated_book = service.update(db_obj=book_model, obj_in=book_update)
    
    # Assert
    assert updated_book.id == book_model.id
    assert updated_book.title == update_data["title"]
    assert updated_book.author == update_data["author"]
    assert updated_book.quantity == update_data["quantity"]
    assert updated_book.isbn == book_data["isbn"]  # Non modifié
    assert updated_book.publication_year == book_data["publication_year"]  # Non modifié


def test_delete_book(db_session: Session):
    """
    Test de suppression d'un livre.
    """
    # Arrange
    repository = BookRepository(BookModel, db_session)
    service = BookService(repository)
    
    # Créer un livre pour le test
    book_data = {
        "title": "Book to Delete",
        "author": "Author to Delete",
        "isbn": "9876543210987",
        "publication_year": 2022,
        "quantity": 3
    }
    book_model = BookModel(**book_data)
    db_session.add(book_model)
    db_session.commit()
    db_session.refresh(book_model)
    
    book_id = book_model.id
    
    # Act
    deleted_book = service.remove(id=book_id)
    
    # Assert
    assert deleted_book.id == book_id
    assert deleted_book.title == book_data["title"]
    
    # Vérifier que le livre a bien été supprimé
    book = service.get(id=book_id)
    assert book is None


def test_get_books_by_author(db_session: Session):
    """
    Test de récupération des livres par auteur.
    """
    # Arrange
    repository = BookRepository(BookModel, db_session)
    service = BookService(repository)
    
    # Créer plusieurs livres pour le test
    author = "Test Author for Search"
    books_data = [
        {
            "title": "Book 1",
            "author": author,
            "isbn": "1111111111111",
            "publication_year": 2020,
            "quantity": 1
        },
        {
            "title": "Book 2",
            "author": author,
            "isbn": "2222222222222",
            "publication_year": 2021,
            "quantity": 2
        },
        {
            "title": "Book 3",
            "author": "Different Author",
            "isbn": "3333333333333",
            "publication_year": 2022,
            "quantity": 3
        }
    ]
    
    for book_data in books_data:
        db_session.add(BookModel(**book_data))
    
    db_session.commit()
    
    # Act
    books = service.get_by_author(author=author)
    
    # Assert
    assert len(books) == 2
    assert all(book.author == author for book in books)


def test_search_books(db_session: Session):
    """
    Test de recherche de livres.
    """
    # Arrange
    repository = BookRepository(BookModel, db_session)
    service = BookService(repository)
    
    # Créer plusieurs livres pour le test
    books_data = [
        {
            "title": "Python Programming",
            "author": "John Doe",
            "isbn": "1111111111111",
            "publication_year": 2020,
            "quantity": 1
        },
        {
            "title": "Advanced Python",
            "author": "Jane Smith",
            "isbn": "2222222222222",
            "publication_year": 2021,
            "quantity": 2
        },
        {
            "title": "Java Programming",
            "author": "Bob Johnson",
            "isbn": "3333333333333",
            "publication_year": 2022,
            "quantity": 3
        }
    ]
    
    for book_data in books_data:
        db_session.add(BookModel(**book_data))
    
    db_session.commit()
    
    # Act
    python_books = service.search(query="Python")
    
    # Assert
    assert len(python_books) == 2
    assert all("Python" in book.title for book in python_books)