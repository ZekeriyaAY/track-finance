from app import db
from app.dashboard import bp
from app.models import Transaction, Category, Brand
from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func, extract
import sqlalchemy as sa
from datetime import datetime, timedelta
from calendar import month_name


@bp.route('/dashboard')
@login_required
def dashboard():
    # Get total income and expense
    income = db.session.scalar(
        sa.select(func.sum(Transaction.amount))
        .join(Transaction.category)
        .where(
            Transaction.user_id == current_user.id,
            Category.type == 'Income'
        )
    ) or 0

    expense = db.session.scalar(
        sa.select(func.sum(Transaction.amount))
        .join(Transaction.category)
        .where(
            Transaction.user_id == current_user.id,
            Category.type == 'Expense'
        )
    ) or 0

    # Get counts
    category_count = db.session.scalar(
        sa.select(func.count())
        .select_from(Category)
        .where(
            Category.user_id == current_user.id,
            Category.is_deleted == False
        )
    ) or 0

    brand_count = db.session.scalar(
        sa.select(func.count())
        .select_from(Brand)
        .where(
            Brand.user_id == current_user.id,
            Brand.is_deleted == False
        )
    ) or 0

    # Get recent transactions
    recent_transactions = db.session.scalars(
        sa.select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.timestamp.desc())
        .limit(5)
    ).all()

    # Get monthly data for the last 6 months
    months = []
    monthly_income = []
    monthly_expense = []
    
    for i in range(5, -1, -1):
        date = datetime.now() - timedelta(days=i*30)
        month = date.strftime('%B')
        months.append(month)

        month_income = db.session.scalar(
            sa.select(func.sum(Transaction.amount))
            .join(Transaction.category)
            .where(
                Transaction.user_id == current_user.id,
                Category.type == 'Income',
                extract('month', Transaction.timestamp) == date.month,
                extract('year', Transaction.timestamp) == date.year
            )
        ) or 0
        monthly_income.append(float(month_income))

        month_expense = db.session.scalar(
            sa.select(func.sum(Transaction.amount))
            .join(Transaction.category)
            .where(
                Transaction.user_id == current_user.id,
                Category.type == 'Expense',
                extract('month', Transaction.timestamp) == date.month,
                extract('year', Transaction.timestamp) == date.year
            )
        ) or 0
        monthly_expense.append(float(month_expense))

    # Get category distribution
    category_data = db.session.execute(
        sa.select(Category.name, func.sum(Transaction.amount))
        .join(Transaction.category)
        .where(Transaction.user_id == current_user.id)
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(5)
    ).all()

    category_names = [cat[0] for cat in category_data]
    category_amounts = [float(cat[1]) for cat in category_data]

    return render_template('dashboard.html',
                         title='Dashboard',
                         total_income=income,
                         total_expense=expense,
                         category_count=category_count,
                         brand_count=brand_count,
                         recent_transactions=recent_transactions,
                         months=months,
                         monthly_income=monthly_income,
                         monthly_expense=monthly_expense,
                         category_names=category_names,
                         category_amounts=category_amounts)
