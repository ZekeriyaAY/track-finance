"""Unit tests for all database models."""
import pytest
from datetime import date, datetime, timezone
from sqlalchemy.exc import IntegrityError

from models import db as _db
from models.user import User
from models.category import Category
from models.tag import Tag
from models.cashflow import CashflowTransaction
from models.investment import InvestmentType, InvestmentTransaction
from models.settings import Settings
from models.bank_connection import BankConnection


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestUserModel:
    """Tests for the User authentication model."""

    def test_create_user(self, app, db):
        """Creating a user persists username and hashed password."""
        user = User(username='testuser')
        user.set_password('secret123')
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == 'testuser'
        assert user.password_hash is not None
        assert user.password_hash != 'secret123'

    def test_password_hashing(self, app, db):
        """set_password hashes, check_password verifies correctly."""
        user = User(username='hashtest')
        user.set_password('mypassword')
        db.session.add(user)
        db.session.commit()

        assert user.check_password('mypassword') is True
        assert user.check_password('wrongpassword') is False

    def test_password_change(self, app, db):
        """Changing the password invalidates the old one."""
        user = User(username='changepw')
        user.set_password('old_pw')
        db.session.add(user)
        db.session.commit()

        old_hash = user.password_hash
        user.set_password('new_pw')
        db.session.commit()

        assert user.password_hash != old_hash
        assert user.check_password('new_pw') is True
        assert user.check_password('old_pw') is False

    def test_get_admin_user_returns_first(self, app, db):
        """get_admin_user returns the first user row."""
        u1 = User(username='first')
        u1.set_password('pw')
        u2 = User(username='second')
        u2.set_password('pw')
        db.session.add_all([u1, u2])
        db.session.commit()

        admin = User.get_admin_user()
        assert admin is not None
        assert admin.username == 'first'

    def test_get_admin_user_none_when_empty(self, app, db):
        """get_admin_user returns None when no users exist."""
        assert User.get_admin_user() is None

    def test_create_default_user(self, app, db):
        """create_default_user creates user only when table is empty."""
        user = User.create_default_user('admin', 'admin123')
        assert user is not None
        assert user.username == 'admin'
        assert user.check_password('admin123')

    def test_create_default_user_skips_when_exists(self, app, db):
        """create_default_user returns None if a user already exists."""
        User.create_default_user('first', 'pw')
        result = User.create_default_user('second', 'pw')
        assert result is None
        assert User.query.count() == 1

    def test_duplicate_username_raises(self, app, db):
        """Inserting a duplicate username raises IntegrityError."""
        u1 = User(username='dup')
        u1.set_password('pw')
        db.session.add(u1)
        db.session.commit()

        u2 = User(username='dup')
        u2.set_password('pw')
        db.session.add(u2)
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_repr(self, app, db):
        """User __repr__ contains the username."""
        user = User(username='repruser')
        user.set_password('pw')
        assert 'repruser' in repr(user)


# ---------------------------------------------------------------------------
# Category model
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestCategoryModel:
    """Tests for the hierarchical Category model."""

    def test_create_category(self, app, db):
        """Basic category creation."""
        cat = Category(name='Food')
        db.session.add(cat)
        db.session.commit()

        assert cat.id is not None
        assert cat.name == 'Food'
        assert cat.parent_id is None

    def test_parent_child_relationship(self, app, db, sample_category, sample_subcategory):
        """Parent has subcategories, child has parent reference."""
        assert sample_subcategory in sample_category.subcategories
        assert sample_subcategory.parent.id == sample_category.id

    def test_is_parent_and_is_subcategory(self, app, db, sample_category, sample_subcategory):
        """is_parent / is_subcategory reflect parent_id."""
        assert sample_category.is_parent() is True
        assert sample_category.is_subcategory() is False
        assert sample_subcategory.is_parent() is False
        assert sample_subcategory.is_subcategory() is True

    def test_get_all_transactions_count_empty(self, app, db, sample_category):
        """Counts are zero with no transactions."""
        assert sample_category.get_all_transactions_count() == 0
        assert sample_category.get_income_count() == 0
        assert sample_category.get_expense_count() == 0

    def test_get_expense_count_direct(self, app, db, sample_category):
        """Expense count for a category with direct transactions."""
        txn = CashflowTransaction(
            date=date(2024, 3, 1), type='expense', amount=50.0,
            description='test', category_id=sample_category.id,
        )
        db.session.add(txn)
        db.session.commit()

        assert sample_category.get_expense_count() == 1
        assert sample_category.get_income_count() == 0
        assert sample_category.get_all_transactions_count() == 1

    def test_get_income_count_direct(self, app, db, sample_category):
        """Income count for a category with direct transactions."""
        txn = CashflowTransaction(
            date=date(2024, 3, 1), type='income', amount=1000.0,
            description='salary', category_id=sample_category.id,
        )
        db.session.add(txn)
        db.session.commit()

        assert sample_category.get_income_count() == 1
        assert sample_category.get_expense_count() == 0

    def test_recursive_counts(self, app, db, sample_category, sample_subcategory):
        """Counts recurse into subcategories."""
        # Transaction on parent
        t1 = CashflowTransaction(
            date=date(2024, 1, 1), type='expense', amount=10,
            description='parent-txn', category_id=sample_category.id,
        )
        # Transaction on child
        t2 = CashflowTransaction(
            date=date(2024, 1, 2), type='expense', amount=20,
            description='child-txn', category_id=sample_subcategory.id,
        )
        t3 = CashflowTransaction(
            date=date(2024, 1, 3), type='income', amount=500,
            description='child-income', category_id=sample_subcategory.id,
        )
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        assert sample_category.get_expense_count() == 2  # 1 parent + 1 child
        assert sample_category.get_income_count() == 1   # 1 child
        assert sample_category.get_all_transactions_count() == 3

    def test_multiple_subcategories(self, app, db, sample_category):
        """Parent with multiple subcategories."""
        sub1 = Category(name='Sub A', parent_id=sample_category.id)
        sub2 = Category(name='Sub B', parent_id=sample_category.id)
        db.session.add_all([sub1, sub2])
        db.session.commit()

        assert len(sample_category.subcategories) == 2


# ---------------------------------------------------------------------------
# Tag model
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestTagModel:
    """Tests for the Tag model."""

    def test_create_tag(self, app, db):
        """Basic tag creation."""
        tag = Tag(name='Cash')
        db.session.add(tag)
        db.session.commit()

        assert tag.id is not None
        assert tag.name == 'Cash'

    def test_unique_name(self, app, db):
        """Duplicate tag name raises IntegrityError."""
        db.session.add(Tag(name='UniqueTag'))
        db.session.commit()

        db.session.add(Tag(name='UniqueTag'))
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_income_and_expense_counts(self, app, db, sample_category):
        """get_income_count / get_expense_count filter by transaction type."""
        tag = Tag(name='Counter')
        db.session.add(tag)
        db.session.flush()

        inc = CashflowTransaction(
            date=date(2024, 2, 1), type='income', amount=100,
            description='inc', category_id=sample_category.id,
        )
        inc.tags.append(tag)

        exp1 = CashflowTransaction(
            date=date(2024, 2, 2), type='expense', amount=50,
            description='exp1', category_id=sample_category.id,
        )
        exp1.tags.append(tag)

        exp2 = CashflowTransaction(
            date=date(2024, 2, 3), type='expense', amount=30,
            description='exp2', category_id=sample_category.id,
        )
        exp2.tags.append(tag)

        db.session.add_all([inc, exp1, exp2])
        db.session.commit()

        assert tag.get_income_count() == 1
        assert tag.get_expense_count() == 2

    def test_tag_no_transactions(self, app, db, sample_tag):
        """Counts are zero when tag has no transactions."""
        assert sample_tag.get_income_count() == 0
        assert sample_tag.get_expense_count() == 0


# ---------------------------------------------------------------------------
# CashflowTransaction model
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestCashflowTransactionModel:
    """Tests for the CashflowTransaction model."""

    def test_create_transaction(self, app, db, sample_category):
        """Basic transaction creation with required fields."""
        txn = CashflowTransaction(
            date=date(2024, 6, 15), type='expense', amount=250.75,
            description='Groceries', category_id=sample_category.id,
        )
        db.session.add(txn)
        db.session.commit()

        assert txn.id is not None
        assert txn.amount == 250.75
        assert txn.type == 'expense'
        assert txn.source == 'manual'

    def test_default_source_is_manual(self, app, db, sample_category):
        """Source defaults to 'manual' when not specified."""
        txn = CashflowTransaction(
            date=date(2024, 1, 1), type='income', amount=100,
            description='test', category_id=sample_category.id,
        )
        db.session.add(txn)
        db.session.commit()
        assert txn.source == 'manual'

    def test_source_types(self, app, db, sample_category):
        """All source types can be set."""
        for src in ['manual', 'excel_import', 'bank_sync']:
            txn = CashflowTransaction(
                date=date(2024, 1, 1), type='expense', amount=10,
                description=f'src-{src}', category_id=sample_category.id,
                source=src,
            )
            db.session.add(txn)
        db.session.commit()

        assert CashflowTransaction.query.filter_by(source='manual').count() == 1
        assert CashflowTransaction.query.filter_by(source='excel_import').count() == 1
        assert CashflowTransaction.query.filter_by(source='bank_sync').count() == 1

    def test_tags_m2m(self, app, db, sample_category):
        """Many-to-many tag relationship works in both directions."""
        tag1 = Tag(name='Tag1')
        tag2 = Tag(name='Tag2')
        db.session.add_all([tag1, tag2])
        db.session.flush()

        txn = CashflowTransaction(
            date=date(2024, 1, 1), type='expense', amount=50,
            description='multi-tag', category_id=sample_category.id,
        )
        txn.tags = [tag1, tag2]
        db.session.add(txn)
        db.session.commit()

        assert len(txn.tags) == 2
        assert txn in tag1.transactions
        assert txn in tag2.transactions

    def test_category_relationship(self, app, db, sample_category):
        """Transaction belongs to its category."""
        txn = CashflowTransaction(
            date=date(2024, 3, 1), type='expense', amount=10,
            description='cat-test', category_id=sample_category.id,
        )
        db.session.add(txn)
        db.session.commit()

        assert txn.category.id == sample_category.id
        assert txn in sample_category.transactions

    def test_unique_constraint_external_txn_bank(self, app, db, sample_category):
        """Duplicate (external_transaction_id, bank_connection_id) raises IntegrityError."""
        bank = BankConnection(
            bank_code='test', bank_name='Test Bank',
        )
        db.session.add(bank)
        db.session.flush()

        txn1 = CashflowTransaction(
            date=date(2024, 1, 1), type='expense', amount=10,
            description='dup1', category_id=sample_category.id,
            external_transaction_id='EXT-001',
            bank_connection_id=bank.id,
        )
        db.session.add(txn1)
        db.session.commit()

        txn2 = CashflowTransaction(
            date=date(2024, 1, 2), type='expense', amount=20,
            description='dup2', category_id=sample_category.id,
            external_transaction_id='EXT-001',
            bank_connection_id=bank.id,
        )
        db.session.add(txn2)
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_unique_constraint_allows_null_pair(self, app, db, sample_category):
        """Two transactions with NULL external_transaction_id are allowed."""
        txn1 = CashflowTransaction(
            date=date(2024, 1, 1), type='expense', amount=10,
            description='null-a', category_id=sample_category.id,
        )
        txn2 = CashflowTransaction(
            date=date(2024, 1, 2), type='expense', amount=20,
            description='null-b', category_id=sample_category.id,
        )
        db.session.add_all([txn1, txn2])
        db.session.commit()  # should not raise

        assert CashflowTransaction.query.count() == 2

    def test_unique_constraint_different_bank(self, app, db, sample_category):
        """Same external_transaction_id with different bank_connection_id is allowed."""
        bank1 = BankConnection(bank_code='b1', bank_name='Bank 1')
        bank2 = BankConnection(bank_code='b2', bank_name='Bank 2')
        db.session.add_all([bank1, bank2])
        db.session.flush()

        txn1 = CashflowTransaction(
            date=date(2024, 1, 1), type='expense', amount=10,
            description='txn1', category_id=sample_category.id,
            external_transaction_id='EXT-001', bank_connection_id=bank1.id,
        )
        txn2 = CashflowTransaction(
            date=date(2024, 1, 1), type='expense', amount=10,
            description='txn2', category_id=sample_category.id,
            external_transaction_id='EXT-001', bank_connection_id=bank2.id,
        )
        db.session.add_all([txn1, txn2])
        db.session.commit()  # should not raise

        assert CashflowTransaction.query.count() == 2


# ---------------------------------------------------------------------------
# InvestmentType model
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestInvestmentTypeModel:
    """Tests for the hierarchical InvestmentType model."""

    def test_create_investment_type(self, app, db):
        """Basic creation with all fields."""
        it = InvestmentType(
            name='Gold', code='gold',
            icon='fas fa-coins', color='#FCD34D',
        )
        db.session.add(it)
        db.session.commit()

        assert it.id is not None
        assert it.name == 'Gold'
        assert it.code == 'gold'
        assert it.created_at is not None

    def test_code_uniqueness(self, app, db):
        """Duplicate code raises IntegrityError."""
        db.session.add(InvestmentType(name='A', code='dup_code', icon='i', color='#000'))
        db.session.commit()

        db.session.add(InvestmentType(name='B', code='dup_code', icon='i', color='#000'))
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_hierarchy(self, app, db, sample_investment_type):
        """Parent/child relationship through parent_id."""
        child = InvestmentType(
            name='Child Stock', code='child_stock',
            icon='fas fa-chart-line', color='#3B82F6',
            parent_id=sample_investment_type.id,
        )
        db.session.add(child)
        db.session.commit()

        assert child.parent.id == sample_investment_type.id
        assert child in sample_investment_type.children

    def test_default_values(self, app, db):
        """Default icon and color are applied when not specified."""
        it = InvestmentType(name='Default', code='def_test')
        db.session.add(it)
        db.session.commit()

        assert it.icon == 'fas fa-chart-pie'
        assert it.color == '#3B82F6'

    def test_repr(self, app, db, sample_investment_type):
        """__repr__ contains the name."""
        assert 'Test Stock' in repr(sample_investment_type)


# ---------------------------------------------------------------------------
# InvestmentTransaction model
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestInvestmentTransactionModel:
    """Tests for the InvestmentTransaction model."""

    def test_create_transaction(self, app, db, sample_investment_type):
        """Basic creation sets all fields including total_amount."""
        txn = InvestmentTransaction(
            investment_type_id=sample_investment_type.id,
            transaction_date=datetime(2024, 5, 1),
            transaction_type='buy',
            price=100.0,
            quantity=5.0,
            description='Buy gold',
        )
        db.session.add(txn)
        db.session.commit()

        assert txn.id is not None
        assert txn.total_amount == 500.0

    def test_total_amount_calculation(self, app, db, sample_investment_type):
        """__init__ correctly calculates total_amount = price * quantity."""
        txn = InvestmentTransaction(
            investment_type_id=sample_investment_type.id,
            transaction_date=datetime(2024, 6, 1),
            transaction_type='sell',
            price=33.33,
            quantity=3.0,
        )
        db.session.add(txn)
        db.session.commit()

        assert abs(txn.total_amount - 99.99) < 0.001

    def test_total_amount_zero_quantity(self, app, db, sample_investment_type):
        """Zero quantity yields zero total_amount."""
        txn = InvestmentTransaction(
            investment_type_id=sample_investment_type.id,
            transaction_date=datetime(2024, 1, 1),
            transaction_type='buy',
            price=100.0,
            quantity=0.0,
        )
        db.session.add(txn)
        db.session.commit()

        assert txn.total_amount == 0.0

    def test_investment_type_relationship(self, app, db, sample_investment_type):
        """Transaction links back to its InvestmentType."""
        txn = InvestmentTransaction(
            investment_type_id=sample_investment_type.id,
            transaction_date=datetime(2024, 1, 1),
            transaction_type='buy',
            price=10.0, quantity=1.0,
        )
        db.session.add(txn)
        db.session.commit()

        assert txn.investment_type.id == sample_investment_type.id
        assert txn in sample_investment_type.investments

    def test_buy_and_sell_types(self, app, db, sample_investment_type):
        """Both transaction types persist correctly."""
        buy = InvestmentTransaction(
            investment_type_id=sample_investment_type.id,
            transaction_date=datetime(2024, 1, 1),
            transaction_type='buy', price=10, quantity=1,
        )
        sell = InvestmentTransaction(
            investment_type_id=sample_investment_type.id,
            transaction_date=datetime(2024, 2, 1),
            transaction_type='sell', price=12, quantity=1,
        )
        db.session.add_all([buy, sell])
        db.session.commit()

        assert buy.transaction_type == 'buy'
        assert sell.transaction_type == 'sell'

    def test_timestamps(self, app, db, sample_investment_type):
        """created_at is set on creation."""
        txn = InvestmentTransaction(
            investment_type_id=sample_investment_type.id,
            transaction_date=datetime(2024, 1, 1),
            transaction_type='buy', price=10, quantity=1,
        )
        db.session.add(txn)
        db.session.commit()

        assert txn.created_at is not None


# ---------------------------------------------------------------------------
# Settings model
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestSettingsModel:
    """Tests for the key-value Settings model."""

    def test_set_and_get_setting(self, app, db):
        """set_setting creates a new row, get_setting retrieves it."""
        Settings.set_setting('theme', 'dark')
        assert Settings.get_setting('theme') == 'dark'

    def test_get_setting_default(self, app, db):
        """get_setting returns default when key does not exist."""
        assert Settings.get_setting('nonexistent') is None
        assert Settings.get_setting('nonexistent', 'fallback') == 'fallback'

    def test_upsert_pattern(self, app, db):
        """set_setting updates an existing key rather than creating duplicate."""
        Settings.set_setting('counter', '1')
        Settings.set_setting('counter', '2')

        assert Settings.get_setting('counter') == '2'
        assert Settings.query.filter_by(key='counter').count() == 1

    def test_multiple_keys(self, app, db):
        """Multiple distinct keys can coexist."""
        Settings.set_setting('key_a', 'value_a')
        Settings.set_setting('key_b', 'value_b')

        assert Settings.get_setting('key_a') == 'value_a'
        assert Settings.get_setting('key_b') == 'value_b'

    def test_value_can_be_none(self, app, db):
        """Setting a value to None is stored and retrieved."""
        Settings.set_setting('nullable', None)
        assert Settings.get_setting('nullable') is None

    def test_repr(self, app, db):
        """__repr__ includes key and value."""
        s = Settings.set_setting('repr_key', 'repr_val')
        r = repr(s)
        assert 'repr_key' in r
        assert 'repr_val' in r

    def test_timestamps(self, app, db):
        """created_at and updated_at are populated."""
        s = Settings.set_setting('ts_key', 'ts_val')
        assert s.created_at is not None


# ---------------------------------------------------------------------------
# BankConnection model
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestBankConnectionModel:
    """Tests for BankConnection with encrypted credentials."""

    def test_create_bank_connection(self, app, db):
        """Basic creation with required fields."""
        bc = BankConnection(
            bank_code='yapikredi',
            bank_name='Yapi Kredi',
        )
        db.session.add(bc)
        db.session.commit()

        assert bc.id is not None
        assert bc.bank_code == 'yapikredi'
        assert bc.is_active is True

    def test_encrypt_decrypt_client_id(self, app, db):
        """set_client_id / get_client_id roundtrip."""
        bc = BankConnection(bank_code='test', bank_name='Test')
        bc.set_client_id('my-client-id')
        db.session.add(bc)
        db.session.commit()

        assert bc.client_id_encrypted is not None
        assert bc.client_id_encrypted != 'my-client-id'
        assert bc.get_client_id() == 'my-client-id'

    def test_encrypt_decrypt_client_secret(self, app, db):
        """set_client_secret / get_client_secret roundtrip."""
        bc = BankConnection(bank_code='test', bank_name='Test')
        bc.set_client_secret('super-secret')
        db.session.add(bc)
        db.session.commit()

        assert bc.client_secret_encrypted is not None
        assert bc.client_secret_encrypted != 'super-secret'
        assert bc.get_client_secret() == 'super-secret'

    def test_none_credentials(self, app, db):
        """get_* returns None when encrypted value is None."""
        bc = BankConnection(bank_code='test', bank_name='Test')
        db.session.add(bc)
        db.session.commit()

        assert bc.get_client_id() is None
        assert bc.get_client_secret() is None

    def test_empty_string_credentials(self, app, db):
        """Setting empty string returns None (encrypt_value returns None for empty)."""
        bc = BankConnection(bank_code='test', bank_name='Test')
        bc.set_client_id('')
        bc.set_client_secret('')
        db.session.add(bc)
        db.session.commit()

        assert bc.get_client_id() is None
        assert bc.get_client_secret() is None

    def test_is_active_default(self, app, db):
        """is_active defaults to True."""
        bc = BankConnection(bank_code='test', bank_name='Test')
        db.session.add(bc)
        db.session.commit()
        assert bc.is_active is True

    def test_sync_status_fields(self, app, db):
        """Sync metadata fields can be set."""
        bc = BankConnection(bank_code='test', bank_name='Test')
        bc.last_sync_status = 'success'
        bc.last_sync_message = '5 new, 0 skipped'
        bc.last_sync_at = datetime.now(timezone.utc)
        db.session.add(bc)
        db.session.commit()

        fetched = BankConnection.query.get(bc.id)
        assert fetched.last_sync_status == 'success'
        assert fetched.last_sync_message == '5 new, 0 skipped'
        assert fetched.last_sync_at is not None

    def test_transactions_relationship(self, app, db, sample_category):
        """BankConnection.transactions dynamic relationship."""
        bc = BankConnection(bank_code='test', bank_name='Test')
        db.session.add(bc)
        db.session.flush()

        txn = CashflowTransaction(
            date=date(2024, 1, 1), type='expense', amount=100,
            description='bank-txn', category_id=sample_category.id,
            bank_connection_id=bc.id,
            external_transaction_id='EXT-1', source='bank_sync',
        )
        db.session.add(txn)
        db.session.commit()

        assert bc.transactions.count() == 1
        assert bc.transactions.first().description == 'bank-txn'

    def test_repr(self, app, db):
        """__repr__ contains bank_name and bank_code."""
        bc = BankConnection(bank_code='yk', bank_name='Yapi Kredi')
        r = repr(bc)
        assert 'Yapi Kredi' in r
        assert 'yk' in r
