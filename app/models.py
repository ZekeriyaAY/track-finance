from app import db
from app import login
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
from hashlib import md5


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    created_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    last_seen: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    preferences: so.Mapped[dict] = so.mapped_column(
        sa.JSON, default=dict)

    transactions: so.WriteOnlyMapped['Transaction'] = so.relationship(
        back_populates='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def update_last_seen(self):
        self.last_seen = datetime.now(timezone.utc)
        db.session.commit()

    def set_preference(self, key, value):
        if not self.preferences:
            self.preferences = {}
        self.preferences[key] = value
        db.session.commit()

    def get_preference(self, key, default=None):
        return self.preferences.get(key, default) if self.preferences else default


class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True, nullable=False)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, nullable=False)
    type: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, nullable=False, default='Expense')
    is_deleted: so.Mapped[bool] = so.mapped_column(default=False)
    deleted_at: so.Mapped[Optional[datetime]] = so.mapped_column(default=None)
    original_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))

    transactions: so.WriteOnlyMapped['Transaction'] = so.relationship(
        back_populates='category',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Category {self.name}>'

    @property
    def transaction_count(self):
        """Bu kategorinin kullanıldığı transaction sayısı"""
        return db.session.scalar(
            sa.select(sa.func.count())
            .where(Transaction.category_id == self.id)
        ) or 0

    def soft_delete(self):
        if self.is_deleted:
            raise ValueError("This category is already deleted")
        
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.original_name = self.name
        self.name = f"DELETED: {self.name} ({self.deleted_at.strftime('%Y-%m-%d')})"

    def restore(self):
        if not self.is_deleted:
            raise ValueError("This category is not deleted")
        
        self.is_deleted = False
        self.deleted_at = None
        self.name = self.original_name
        self.original_name = None
        self.timestamp = datetime.now(timezone.utc)
        
        db.session.flush()


class Brand(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True, nullable=False)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, nullable=False)
    is_deleted: so.Mapped[bool] = so.mapped_column(default=False)
    deleted_at: so.Mapped[Optional[datetime]] = so.mapped_column(default=None)
    original_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))

    transactions: so.WriteOnlyMapped['Transaction'] = so.relationship(
        back_populates='brand',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Brand {self.name}>'

    @property
    def transaction_count(self):
        """Bu brand'in kullanıldığı transaction sayısı"""
        return db.session.scalar(
            sa.select(sa.func.count())
            .where(Transaction.brand_id == self.id)
        ) or 0

    def soft_delete(self):
        if self.is_deleted:
            raise ValueError("This brand is already deleted")
        
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.original_name = self.name
        self.name = f"DELETED: {self.name} ({self.deleted_at.strftime('%Y-%m-%d')})"

    def restore(self):
        if not self.is_deleted:
            raise ValueError("This brand is not deleted")
        
        self.is_deleted = False
        self.deleted_at = None
        self.name = self.original_name
        self.original_name = None
        self.timestamp = datetime.now(timezone.utc)
        
        db.session.flush()


class Transaction(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True, nullable=False)
    category_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Category.id), index=True, nullable=False)
    brand_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Brand.id, ondelete='CASCADE'),
        index=True,
        nullable=False
    )
    name: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    amount: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Float, nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))

    user: so.Mapped[User] = so.relationship(back_populates='transactions')
    category: so.Mapped[Category] = so.relationship(
        back_populates='transactions')
    brand: so.Mapped[Brand] = so.relationship(back_populates='transactions')

    def __repr__(self):
        return f'<Transaction {self.name}>'
