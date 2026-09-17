from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pirddiiqlab.backend import db


class MovementType(str, Enum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    DISPOSAL = "disposal"


class InventoryItem(db.Model):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    reorder_threshold: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False, default=Decimal("0")
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    lots: Mapped[list["InventoryLot"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("reorder_threshold >= 0", name="ck_item_reorder_threshold_nonnegative"),
        Index("ix_inventory_items_category_active", "category", "is_active"),
    )


class InventoryLot(db.Model):
    __tablename__ = "inventory_lots"

    id: Mapped[int] = mapped_column(primary_key=True)
    inventory_item_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_items.id", ondelete="RESTRICT"),
        nullable=False,
    )
    lot_number: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_on_hand: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False, default=Decimal("0")
    )
    expiration_date: Mapped[date | None] = mapped_column()
    storage_location: Mapped[str] = mapped_column(String(255), nullable=False)
    received_at: Mapped[datetime | None] = mapped_column()
    is_quarantined: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    item: Mapped["InventoryItem"] = relationship(back_populates="lots")
    movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="lot",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint("quantity_on_hand >= 0", name="ck_lot_quantity_nonnegative"),
        Index("ix_inventory_lots_expiration_date", "expiration_date"),
        Index("ix_inventory_lots_item_location", "inventory_item_id", "storage_location"),
        db.UniqueConstraint(
            "inventory_item_id",
            "lot_number",
            "storage_location",
            name="uq_inventory_lot_item_number_location",
        ),
    )


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    inventory_lot_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_lots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    from_location: Mapped[str | None] = mapped_column(String(255))
    to_location: Mapped[str | None] = mapped_column(String(255))
    reference: Mapped[str | None] = mapped_column(String(255))
    reason: Mapped[str | None] = mapped_column(Text)
    performed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    lot: Mapped["InventoryLot"] = relationship(back_populates="movements")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_movement_quantity_positive"),
        CheckConstraint(
            "movement_type IN "
            "('receipt', 'issue', 'transfer', 'adjustment', 'disposal')",
            name="ck_movement_type_valid",
        ),
        Index("ix_stock_movements_lot_occurred", "inventory_lot_id", "occurred_at"),
        Index("ix_stock_movements_reference", "reference"),
    )
