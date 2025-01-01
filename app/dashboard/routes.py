from app import db
from app.dashboard import bp
from app.models import Transaction, Category
from flask import render_template
from flask_login import login_required, current_user
import sqlalchemy as sa


@bp.route('/dashboard')
@login_required
def dashboard():
    # Toplam istatistikler
    total_transactions = db.session.scalar(
        sa.select(sa.func.count()).select_from(Transaction)
        .where(Transaction.user_id == current_user.id)
    ) or 0
    
    total_expenses = db.session.scalar(
        sa.select(sa.func.sum(Transaction.amount))
        .join(Category)
        .where(
            Transaction.user_id == current_user.id,
            Category.type == 'Expense'
        )
    ) or 0
    
    total_income = db.session.scalar(
        sa.select(sa.func.sum(Transaction.amount))
        .join(Category)
        .where(
            Transaction.user_id == current_user.id,
            Category.type == 'Income'
        )
    ) or 0
    
    net_amount = total_income - total_expenses
    
    # Son transactionlar
    recent_transactions = db.session.scalars(
        sa.select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.timestamp.desc())
        .limit(5)
    ).all()
    
    # En çok kullanılan kategoriler
    top_categories = db.session.execute(
        sa.select(
            Category.name,
            Category.type,
            sa.func.count().label('count'),
            sa.func.sum(Transaction.amount).label('total')
        )
        .join(Transaction)
        .where(Category.user_id == current_user.id)
        .group_by(Category.id)
        .order_by(sa.text('count DESC'))
        .limit(5)
    ).all()
    
    return render_template('index.html', title='Dashboard',
                         total_transactions=total_transactions,
                         total_expenses=total_expenses,
                         total_income=total_income,
                         net_amount=net_amount,
                         recent_transactions=recent_transactions,
                         top_categories=top_categories) 