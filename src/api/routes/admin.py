from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ...models import User, Loan
from typing import List

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/users_loans")
def list_users_loans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    users = db.query(User).all()
    results = []
    for user in users:
        loans = db.query(Loan).filter(Loan.user_id == user.id).all()
        results.append({
            "user": {"id": user.id, "email": user.email},
            "loans": [{"book_id": loan.book_id, "due_date": loan.due_date, "return_date": loan.return_date} for loan in loans]
        })
    return results
