from flask import Blueprint, render_template
from models.cashflow import CashflowTransaction
from sqlalchemy import extract, func
from models.__init__ import db
from models.category import Category


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/cashflow')
def dashboard_cashflow():
    # Aylara göre gelir ve gider toplamlarını çek
    results = db.session.query(
        extract('year', CashflowTransaction.date).label('year'),
        extract('month', CashflowTransaction.date).label('month'),
        CashflowTransaction.type,
        func.sum(CashflowTransaction.amount).label('total')
    ).group_by('year', 'month', CashflowTransaction.type).order_by('year', 'month').all()

    # Sonuçları frontend için işleyelim
    monthly_data = {}
    for year, month, ttype, total in results:
        key = f"{int(year)}-{int(month):02d}"
        if key not in monthly_data:
            monthly_data[key] = {'income': 0, 'expense': 0}
        monthly_data[key][ttype] = float(total)

    # Grafik için x ve y eksenlerini hazırla
    labels = sorted(monthly_data.keys())
    income = [monthly_data[label]['income'] for label in labels]
    expense = [monthly_data[label]['expense'] for label in labels]

    # Kategoriye göre gelir ve gider toplamlarını çek
    category_results = db.session.query(
        Category.name,
        CashflowTransaction.type,
        func.sum(CashflowTransaction.amount)
    ).join(Category, CashflowTransaction.category_id == Category.id).group_by(Category.name, CashflowTransaction.type).all()

    # Sonuçları frontend için işleyelim
    category_data = {}
    for cat_name, ttype, total in category_results:
        if cat_name not in category_data:
            category_data[cat_name] = {'income': 0, 'expense': 0}
        category_data[cat_name][ttype] = float(total)

    category_labels = list(category_data.keys())
    category_income = [category_data[label]['income'] if category_data[label]['income'] is not None else 0 for label in category_labels]
    category_expense = [category_data[label]['expense'] if category_data[label]['expense'] is not None else 0 for label in category_labels]

    # Toplam gelir, gider ve net bakiye
    total_income = db.session.query(func.sum(CashflowTransaction.amount)).filter(CashflowTransaction.type == 'income').scalar() or 0
    total_expense = db.session.query(func.sum(CashflowTransaction.amount)).filter(CashflowTransaction.type == 'expense').scalar() or 0
    net_balance = total_income - total_expense

    # En çok harcama yapılan ilk 5 kategori (gider)
    top_expense_results = db.session.query(
        Category.name,
        func.sum(CashflowTransaction.amount).label('total_expense')
    ).join(Category, CashflowTransaction.category_id == Category.id).filter(CashflowTransaction.type == 'expense').group_by(Category.name).order_by(func.sum(CashflowTransaction.amount).desc()).limit(5).all()

    top_expense_labels = [row[0] for row in top_expense_results]
    top_expense_values = [float(row[1]) for row in top_expense_results]

    return render_template(
        'dashboard/cashflow.html',
        labels=labels,
        income=income,
        expense=expense,
        category_labels=category_labels,
        category_income=category_income,
        category_expense=category_expense,
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        top_expense_labels=top_expense_labels,
        top_expense_values=top_expense_values
    ) 