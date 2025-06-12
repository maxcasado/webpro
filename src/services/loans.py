from typing import List, Optional, Any, Dict, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..repositories.loans import LoanRepository
from ..repositories.books import BookRepository
from ..repositories.users import UserRepository
from ..models.loans import Loan
from ..models.books import Book
from ..models.users import User
from ..api.schemas.loans import LoanCreate, LoanUpdate
from .base import BaseService


class LoanService(BaseService[Loan, LoanCreate, LoanUpdate]):
    """
    Service pour la gestion des emprunts.
    """
    def __init__(
        self,
        loan_repository: LoanRepository,
        book_repository: BookRepository,
        user_repository: UserRepository
    ):
        super().__init__(loan_repository)
        self.loan_repository = loan_repository
        self.book_repository = book_repository
        self.user_repository = user_repository
    
    def get_active_loans(self) -> List[Loan]:
        """
        Récupère les emprunts actifs (non retournés).
        """
        return self.loan_repository.get_active_loans()
    
    def get_overdue_loans(self) -> List[Loan]:
        """
        Récupère les emprunts en retard.
        """
        return self.loan_repository.get_overdue_loans()
    
    def get_loans_by_user(self, *, user_id: int) -> List[Loan]:
        """
        Récupère les emprunts d'un utilisateur.
        """
        return self.loan_repository.get_loans_by_user(user_id=user_id)
    
    def get_loans_by_book(self, *, book_id: int) -> List[Loan]:
        """
        Récupère les emprunts d'un livre.
        """
        return self.loan_repository.get_loans_by_book(book_id=book_id)
    
    def create_loan(
        self,
        *,
        user_id: int,
        book_id: int,
        loan_period_days: int = 14
    ) -> Loan:
        """
        Crée un nouvel emprunt, en vérifiant la disponibilité du livre et en appliquant les règles métier.
        """
        # Vérifier que l'utilisateur existe
        user = self.user_repository.get(id=user_id)
        if not user:
            raise ValueError(f"Utilisateur avec l'ID {user_id} non trouvé")
        
        # Vérifier que l'utilisateur est actif
        if not user.is_active:
            raise ValueError("L'utilisateur est inactif et ne peut pas emprunter de livres")
        
        # Vérifier que le livre existe
        book = self.book_repository.get(id=book_id)
        if not book:
            raise ValueError(f"Livre avec l'ID {book_id} non trouvé")
        
        # Vérifier que le livre est disponible
        if book.quantity <= 0:
            raise ValueError("Le livre n'est pas disponible pour l'emprunt")
        
        # Vérifier si l'utilisateur a déjà emprunté ce livre et ne l'a pas rendu
        active_loans = self.loan_repository.get_active_loans()
        for loan in active_loans:
            if loan.user_id == user_id and loan.book_id == book_id:
                raise ValueError("L'utilisateur a déjà emprunté ce livre et ne l'a pas encore rendu")
        
        # Vérifier le nombre d'emprunts actifs de l'utilisateur (limite à 5 par exemple)
        user_active_loans = [loan for loan in active_loans if loan.user_id == user_id]
        if len(user_active_loans) >= 5:
            raise ValueError("L'utilisateur a atteint la limite d'emprunts simultanés (5)")
        
        # Créer l'emprunt
        loan_data = {
            "user_id": user_id,
            "book_id": book_id,
            "loan_date": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(days=loan_period_days),
            "return_date": None
        }
        
        loan = self.loan_repository.create(obj_in=loan_data)
        
        # Mettre à jour la quantité de livres disponibles
        book.quantity -= 1
        self.book_repository.update(db_obj=book, obj_in={"quantity": book.quantity})
        
        return loan
    
    def return_loan(self, *, loan_id: int) -> Loan:
        """
        Marque un emprunt comme retourné et met à jour la quantité de livres disponibles.
        """
        # Récupérer l'emprunt
        loan = self.loan_repository.get(id=loan_id)
        if not loan:
            raise ValueError(f"Emprunt avec l'ID {loan_id} non trouvé")
        
        # Vérifier si l'emprunt est déjà retourné
        if loan.return_date:
            raise ValueError("L'emprunt a déjà été retourné")
        
        # Marquer l'emprunt comme retourné
        loan_data = {"return_date": datetime.utcnow()}
        loan = self.loan_repository.update(db_obj=loan, obj_in=loan_data)
        
        # Mettre à jour la quantité de livres disponibles
        book = self.book_repository.get(id=loan.book_id)
        if book:
            book.quantity += 1
            self.book_repository.update(db_obj=book, obj_in={"quantity": book.quantity})
        
        return loan
    
    def extend_loan(self, *, loan_id: int, extension_days: int = 7) -> Loan:
        """
        Prolonge la durée d'un emprunt, en vérifiant les règles métier.
        """
        # Récupérer l'emprunt
        loan = self.loan_repository.get(id=loan_id)
        if not loan:
            raise ValueError(f"Emprunt avec l'ID {loan_id} non trouvé")
        
        # Vérifier si l'emprunt est déjà retourné
        if loan.return_date:
            raise ValueError("L'emprunt a déjà été retourné")
        
        # Vérifier si l'emprunt est en retard
        if loan.due_date < datetime.utcnow():
            raise ValueError("L'emprunt est en retard et ne peut pas être prolongé")
        
        # Vérifier si l'emprunt a déjà été prolongé (en supposant qu'on ne peut prolonger qu'une fois)
        # Cette vérification est simplifiée, vous pourriez ajouter un champ "extensions_count" au modèle Loan
        if loan.due_date > loan.loan_date + timedelta(days=14):
            raise ValueError("L'emprunt a déjà été prolongé")
        
        # Prolonger l'emprunt
        new_due_date = loan.due_date + timedelta(days=extension_days)
        loan_data = {"due_date": new_due_date}
        
        return self.loan_repository.update(db_obj=loan, obj_in=loan_data)