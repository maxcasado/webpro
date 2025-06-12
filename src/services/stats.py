from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.books import Book
from ..models.users import User
from ..models.loans import Loan


class StatsService:
    """
    Service pour les statistiques de la bibliothèque.
    """
    def __init__(self, db: Session):
        self.db = db
    
    def get_general_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques générales sur la bibliothèque.
        """
        total_books = self.db.query(func.sum(Book.quantity)).scalar() or 0
        unique_books = self.db.query(func.count(Book.id)).scalar() or 0
        total_users = self.db.query(func.count(User.id)).scalar() or 0
        active_users = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        total_loans = self.db.query(func.count(Loan.id)).scalar() or 0
        active_loans = self.db.query(func.count(Loan.id)).filter(Loan.return_date == None).scalar() or 0
        overdue_loans = self.db.query(func.count(Loan.id)).filter(
            Loan.return_date == None,
            Loan.due_date < datetime.utcnow()
        ).scalar() or 0
        
        return {
            "total_books": total_books,
            "unique_books": unique_books,
            "total_users": total_users,
            "active_users": active_users,
            "total_loans": total_loans,
            "active_loans": active_loans,
            "overdue_loans": overdue_loans
        }
    
    def get_most_borrowed_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les livres les plus empruntés.
        """
        result = self.db.query(
            Book.id,
            Book.title,
            Book.author,
            func.count(Loan.id).label("loan_count")
        ).join(Loan).group_by(Book.id).order_by(func.count(Loan.id).desc()).limit(limit).all()
        
        return [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "loan_count": book.loan_count
            }
            for book in result
        ]
    
    def get_most_active_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les utilisateurs les plus actifs.
        """
        result = self.db.query(
            User.id,
            User.full_name,
            User.email,
            func.count(Loan.id).label("loan_count")
        ).join(Loan).group_by(User.id).order_by(func.count(Loan.id).desc()).limit(limit).all()
        
        return [
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "loan_count": user.loan_count
            }
            for user in result
        ]
    
    def get_monthly_loans(self, months: int = 12) -> List[Dict[str, Any]]:
        """
        Récupère le nombre d'emprunts par mois pour les derniers mois.
        """
        start_date = datetime.utcnow() - timedelta(days=30 * months)
        
        # Cette requête est simplifiée et peut ne pas fonctionner avec tous les SGBD
        # Pour une solution plus robuste, utilisez des fonctions spécifiques au SGBD
        result = self.db.query(
            func.strftime("%Y-%m", Loan.loan_date).label("month"),
            func.count(Loan.id).label("loan_count")
        ).filter(
            Loan.loan_date >= start_date
        ).group_by(
            func.strftime("%Y-%m", Loan.loan_date)
        ).order_by(
            func.strftime("%Y-%m", Loan.loan_date)
        ).all()
        
        return [
            {
                "month": month,
                "loan_count": loan_count
            }
            for month, loan_count in result
        ]