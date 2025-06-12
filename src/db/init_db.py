import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..models.users import User
from ..models.books import Book
from ..models.loans import Loan
from ..models.categories import Category
from ..utils.security import get_password_hash

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """
    Initialise la base de données avec des données de test.
    """
    # Créer un administrateur
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin_data = {
            "email": "admin@example.com",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "Admin User",
            "is_active": True,
            "is_admin": True,
        }
        admin = User(**admin_data)
        db.add(admin)
        db.commit()
        logger.info("Administrateur créé")
    
    # Créer des catégories
    categories = [
        {"name": "Roman", "description": "Romans littéraires"},
        {"name": "Science-Fiction", "description": "Livres de science-fiction"},
        {"name": "Policier", "description": "Romans policiers et thrillers"},
        {"name": "Biographie", "description": "Biographies et autobiographies"},
        {"name": "Histoire", "description": "Livres d'histoire"},
    ]
    
    for category_data in categories:
        category = db.query(Category).filter(Category.name == category_data["name"]).first()
        if not category:
            category = Category(**category_data)
            db.add(category)
    
    db.commit()
    logger.info("Catégories créées")
    
    # Récupérer les catégories
    roman = db.query(Category).filter(Category.name == "Roman").first()
    sf = db.query(Category).filter(Category.name == "Science-Fiction").first()
    policier = db.query(Category).filter(Category.name == "Policier").first()
    biographie = db.query(Category).filter(Category.name == "Biographie").first()
    histoire = db.query(Category).filter(Category.name == "Histoire").first()
    
    # Créer des livres
    books = [
        {
            "title": "1984",
            "author": "George Orwell",
            "isbn": "9780451524935",
            "publication_year": 1949,
            "description": "Un roman dystopique sur un régime totalitaire",
            "quantity": 5,
            "publisher": "Secker & Warburg",
            "language": "Anglais",
            "pages": 328,
            "categories": [roman, sf]
        },
        {
            "title": "Le Seigneur des Anneaux",
            "author": "J.R.R. Tolkien",
            "isbn": "9780618640157",
            "publication_year": 1954,
            "description": "Une épopée de fantasy",
            "quantity": 3,
            "publisher": "Allen & Unwin",
            "language": "Anglais",
            "pages": 1178,
            "categories": [roman, sf]
        },
        {
            "title": "Le Nom de la Rose",
            "author": "Umberto Eco",
            "isbn": "9782253033134",
            "publication_year": 1980,
            "description": "Un roman policier médiéval",
            "quantity": 2,
            "publisher": "Grasset",
            "language": "Italien",
            "pages": 512,
            "categories": [roman, policier, histoire]
        },
        {
            "title": "Steve Jobs",
            "author": "Walter Isaacson",
            "isbn": "9781451648539",
            "publication_year": 2011,
            "description": "La biographie de Steve Jobs",
            "quantity": 4,
            "publisher": "Simon & Schuster",
            "language": "Anglais",
            "pages": 656,
            "categories": [biographie]
        },
    ]
    
    for book_data in books:
        categories = book_data.pop("categories")
        book = db.query(Book).filter(Book.isbn == book_data["isbn"]).first()
        if not book:
            book = Book(**book_data)
            db.add(book)
            db.flush()  # Pour obtenir l'ID du livre
            
            # Ajouter les catégories
            for category in categories:
                book.categories.append(category)
    
    db.commit()
    logger.info("Livres créés")
    
    # Créer un utilisateur normal
    user = db.query(User).filter(User.email == "user@example.com").first()
    if not user:
        user_data = {
            "email": "user@example.com",
            "hashed_password": get_password_hash("user123"),
            "full_name": "Regular User",
            "is_active": True,
            "is_admin": False,
            "phone": "123-456-7890",
            "address": "123 Main St, Anytown, USA"
        }
        user = User(**user_data)
        db.add(user)
        db.commit()
        logger.info("Utilisateur créé")
    
    # Créer des emprunts
    book1 = db.query(Book).filter(Book.isbn == "9780451524935").first()
    book2 = db.query(Book).filter(Book.isbn == "9780618640157").first()
    
    if book1 and book2 and user:
        # Emprunt actif
        loan1 = db.query(Loan).filter(
            Loan.user_id == user.id,
            Loan.book_id == book1.id,
            Loan.return_date == None
        ).first()
        
        if not loan1:
            loan1_data = {
                "user_id": user.id,
                "book_id": book1.id,
                "loan_date": datetime.utcnow() - timedelta(days=7),
                "due_date": datetime.utcnow() + timedelta(days=7),
                "return_date": None,
                "extended": False
            }
            loan1 = Loan(**loan1_data)
            db.add(loan1)
            
            # Mettre à jour la quantité
            book1.quantity -= 1
            db.add(book1)
        
        # Emprunt retourné
        loan2 = db.query(Loan).filter(
            Loan.user_id == user.id,
            Loan.book_id == book2.id,
            Loan.return_date != None
        ).first()
        
        if not loan2:
            loan2_data = {
                "user_id": user.id,
                "book_id": book2.id,
                "loan_date": datetime.utcnow() - timedelta(days=30),
                "due_date": datetime.utcnow() - timedelta(days=16),
                "return_date": datetime.utcnow() - timedelta(days=20),
                "extended": True
            }
            loan2 = Loan(**loan2_data)
            db.add(loan2)
        
        db.commit()
        logger.info("Emprunts créés")