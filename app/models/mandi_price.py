"""SQLAlchemy model for cached Agmarknet mandi prices."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MandiPrice(Base):
    """One market/commodity/variety row from Agmarknet, cached locally."""

    __tablename__ = "mandi_prices"
    __table_args__ = (
        UniqueConstraint(
            "state",
            "district",
            "market",
            "commodity",
            "variety",
            "arrival_date",
            name="uq_mandi_price_row",
        ),
        Index("ix_mandi_prices_lookup", "commodity", "state", "district"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(120), index=True, default="")
    district: Mapped[str] = mapped_column(String(120), index=True, default="")
    market: Mapped[str] = mapped_column(String(160), index=True, default="")
    commodity: Mapped[str] = mapped_column(String(120), index=True, default="")
    variety: Mapped[str] = mapped_column(String(120), default="")
    min_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    modal_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    arrival_date: Mapped[str] = mapped_column(String(32), default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, index=True, default=datetime.utcnow
    )
