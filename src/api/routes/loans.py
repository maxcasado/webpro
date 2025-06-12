from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from datetime import datetime, timedelta

from ...db.session import get_db
from ...models.loans import Loan as LoanModel
from ...models.books import Book as BookModel
from ...models.users import User as UserModel
from ..schemas.loans import Loan, LoanCreate, LoanUpdate
from ...repositories.loans import LoanRepository
from ...repositories.books import BookRepository
from ...repositories.users import UserRepository
from ...services.loans import LoanService
from ..dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=List[Loan])
def read_loans(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère la liste des emprunts.
    """
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    loans = service.get_multi(skip=skip, limit=limit)
    return loans


@router.post("/", response_model=Loan, status_code=status.HTTP_201_CREATED)
def create_loan(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    book_id: int,
    loan_period_days: int = 14,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Crée un nouvel emprunt.
    """
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    
    try:
        loan = service.create_loan(
            user_id=user_id,
            book_id=book_id,
            loan_period_days=loan_period_days
        )
        return loan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{id}", response_model=Loan)
def read_loan(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Récupère un emprunt par son ID.
    """
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    
    loan = service.get(id=id)
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emprunt non trouvé"
        )
    
    # Vérifier que l'utilisateur est l'emprunteur ou un administrateur
    if not current_user.is_admin and current_user.id != loan.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )
    
    return loan


@router.post("/{id}/return", response_model=Loan)
def return_loan(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Marque un emprunt comme retourné.
    """
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    
    try:
        loan = service.return_loan(loan_id=id)
        return loan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{id}/extend", response_model=Loan)
def extend_loan(
    *,
    db: Session = Depends(get_db),
    id: int,
    extension_days: int = 7,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Prolonge la durée d'un emprunt.
    """
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    
    try:
        loan = service.extend_loan(loan_id=id, extension_days=extension_days)
        return loan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/active/", response_model=List[Loan])
def read_active_loans(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère les emprunts actifs (non retournés).
    """
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    
    loans = service.get_active_loans()
    return loans


@router.get("/overdue/", response_model=List[Loan])
def read_overdue_loans(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère les emprunts en retard.
    """
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    
    loans = service.get_overdue_loans()
    return loans


@router.get("/user/{user_id}", response_model=List[Loan])
def read_user_loans(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Récupère les emprunts d'un utilisateur.
    """
    # Vérifier que l'utilisateur est l'emprunteur ou un administrateur
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )
    
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    
    loans = service.get_loans_by_user(user_id=user_id)
    return loans


@router.get("/book/{book_id}", response_model=List[Loan])
def read_book_loans(
    *,
    db: Session = Depends(get_db),
    book_id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère les emprunts d'un livre.
    """
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    
    loans = service.get_loans_by_book(book_id=book_id)
    return loans