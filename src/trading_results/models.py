import datetime

from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class SpimexTrading(Base):
    __tablename__ = 'spimex_trading_results'

    id: Mapped[int] = mapped_column('id', primary_key=True)
    product_id: Mapped[str] = mapped_column('exchange_product_id')
    oil_id: Mapped[str] = mapped_column('oil_id')
    delivery_id: Mapped[str] = mapped_column('delivery_basis_id')
    delivery_type: Mapped[str] = mapped_column('delivery_type_id')
    date: Mapped[datetime.date] = mapped_column('date')