from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Loan(Base):
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    loan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    return_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=False)
    extended = Column(Boolean, default=False, nullable=False)
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('due_date > loan_date', name='check_due_date_after_loan_date'),
        CheckConstraint('return_date IS NULL OR return_date >= loan_date', name='check_return_date_after_loan_date'),
        # Index pour les recherches fréquentes
        Index('idx_loan_user_id', 'user_id'),
        Index('idx_loan_book_id', 'book_id'),
        Index('idx_loan_return_date', 'return_date'),
    )
    
    # Relations
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")