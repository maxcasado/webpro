from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

from .base import BaseRepository
from ..models.loans import Loan
from ..models.books import Book
from ..models.users import User


class LoanRepository(BaseRepository[Loan, None, None]):
    def get_active_loans(self) -> List[Loan]:
        """
        Récupère les emprunts actifs (non retournés).
        """
        return self.db.query(Loan).filter(Loan.return_date == None).all()
    
    def get_overdue_loans(self) -> List[Loan]:
        """
        Récupère les emprunts en retard.
        """
        now = datetime.utcnow()
        return self.db.query(Loan).filter(
            Loan.return_date == None,
            Loan.due_date < now
        ).all()
    
    def get_loans_by_user(self, *, user_id: int) -> List[Loan]:
        """
        Récupère les emprunts d'un utilisateur.
        """
        return self.db.query(Loan).filter(Loan.user_id == user_id).all()
    
    def get_loans_by_book(self, *, book_id: int) -> List[Loan]:
        """
        Récupère les emprunts d'un livre.
        """
        return self.db.query(Loan).filter(Loan.book_id == book_id).all()
    
    def get_with_details(self, *, id: int) -> Optional[Loan]:
        """
        Récupère un emprunt avec les détails du livre et de l'utilisateur.
        """
        return self.db.query(Loan).options(
            joinedload(Loan.user),
            joinedload(Loan.book)
        ).filter(Loan.id == id).first()
    
    def get_multi_with_details(self, *, skip: int = 0, limit: int = 100) -> List[Loan]:
        """
        Récupère plusieurs emprunts avec les détails des livres et des utilisateurs.
        """
        return self.db.query(Loan).options(
            joinedload(Loan.user),
            joinedload(Loan.book)
        ).offset(skip).limit(limit).all()
    
    def get_loans_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur les emprunts.
        """
        now = datetime.utcnow()
        total_loans = self.db.query(func.count(Loan.id)).scalar() or 0
        active_loans = self.db.query(func.count(Loan.id)).filter(Loan.return_date == None).scalar() or 0
        overdue_loans = self.db.query(func.count(Loan.id)).filter(
            Loan.return_date == None,
            Loan.due_date < now
        ).scalar() or 0
        
        # Emprunts par mois (12 derniers mois)
        start_date = now - timedelta(days=365)
        loans_by_month = self.db.query(
            func.strftime("%Y-%m", Loan.loan_date).label("month"),
            func.count(Loan.id).label("count")
        ).filter(
            Loan.loan_date >= start_date
        ).group_by(
            func.strftime("%Y-%m", Loan.loan_date)
        ).all()
        
        loans_by_month_dict = {month: count for month, count in loans_by_month}
        
        return {
            "total_loans": total_loans,
            "active_loans": active_loans,
            "overdue_loans": overdue_loans,
            "loans_by_month": loans_by_month_dict
        }