from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import exists, and_
from backend.models import Transaction, Asset
from .base import TransactionDTO

class TransactionProcessor:
    """
    Handles business logic for processing and inserting transactions.
    """

    def process_transactions(self, transactions: List[TransactionDTO], db_session: Session) -> int:
        """
        Iterates through transactions and inserts valid ones into the database.
        Returns the count of inserted transactions.
        """
        inserted_count = 0
        for dto in transactions:
            if self._is_duplicate(dto, db_session):
                continue

            # Create Transaction ORM object
            txn = Transaction(
                date=dto.date,
                asset_type=dto.asset_type,
                symbol=dto.symbol,
                action=dto.action,
                price=dto.price,
                quantity=dto.quantity,
                contract_month=dto.contract_month,
                multiplier=dto.multiplier,
                fee=dto.fee,
                tax=dto.tax,
                assigned_margin=dto.assigned_margin
            )
            
            db_session.add(txn)
            inserted_count += 1
            
            # Note: Asset position updates (FIFO/Avg Cost) are explicitly excluded 
            # from this task as per requirements.

        db_session.commit()
        return inserted_count

    def _is_duplicate(self, dto: TransactionDTO, session: Session) -> bool:
        """
        Checks if a transaction already exists in the database.
        Idempotency check based on: date, symbol, action, quantity, price.
        """
        # We assume that if a transaction with the exact same details exists, it is a duplicate.
        # This might be partially risky if a user does two identical trades on the same day,
        # but for now, it adheres to the requirement.
        
        stmt = exists().where(
            and_(
                Transaction.date == dto.date,
                Transaction.symbol == dto.symbol,
                Transaction.action == dto.action,
                Transaction.quantity == dto.quantity,
                Transaction.price == dto.price,
                Transaction.asset_type == dto.asset_type
                # We could add fee/tax check if needed, but primary keys are usually date+symbol+action+price+qty
            )
        )
        return session.query(stmt).scalar()
