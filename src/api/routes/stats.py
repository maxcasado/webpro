from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ...db.session import get_db
from ...services.stats import StatsService
from ..dependencies import get_current_admin_user

router = APIRouter()


@router.get("/general", response_model=Dict[str, Any])
def get_general_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère des statistiques générales sur la bibliothèque.
    """
    service = StatsService(db)
    return service.get_general_stats()


@router.get("/most-borrowed-books", response_model=List[Dict[str, Any]])
def get_most_borrowed_books(
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère les livres les plus empruntés.
    """
    service = StatsService(db)
    return service.get_most_borrowed_books(limit=limit)


@router.get("/most-active-users", response_model=List[Dict[str, Any]])
def get_most_active_users(
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère les utilisateurs les plus actifs.
    """
    service = StatsService(db)
    return service.get_most_active_users(limit=limit)


@router.get("/monthly-loans", response_model=List[Dict[str, Any]])
def get_monthly_loans(
    db: Session = Depends(get_db),
    months: int = 12,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère le nombre d'emprunts par mois pour les derniers mois.
    """
    service = StatsService(db)
    return service.get_monthly_loans(months=months)