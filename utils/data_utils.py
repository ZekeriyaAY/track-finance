from datetime import datetime, timedelta
import random
from models.__init__ import db
from models.category import Category
from models.tag import Tag
from models.cashflow import CashflowTransaction
from models.investment import InvestmentType, InvestmentTransaction

def create_default_categories():
    """Creates default income and expense categories."""
    default_categories = {
        'Income': ['Salary', 'Freelance', 'Rental', 'Refund'],
        'Food & Dining': ['Groceries', 'Restaurants', 'Coffee & Snacks'],
        'Transportation': ['Public Transport', 'Fuel', 'Taxi & Ride Share', 'Parking', 'Vehicle Maintenance', 'Car Insurance', 'Flight'],
        'Housing': ['Rent', 'Property Tax', 'Home Insurance', 'Utilities', 'Maintenance & Repairs'],
        'Shopping': ['Clothing & Shoes', 'Electronics', 'Personal Care', 'Home Supplies', 'Gifts'],
        'Health & Fitness': ['Doctor & Hospital', 'Pharmacy & Medicine', 'Health Insurance', 'Gym & Sports'],
        'Entertainment': ['Movies & Cinema', 'Streaming Services', 'Hobbies', 'Books & Magazines', 'Games', 'Events & Concerts'],
        'Bills & Utilities': ['Electricity', 'Water', 'Gas', 'Internet', 'Mobile Phone'],
        'Education': ['Courses & Training', 'Books & Supplies'],
        'Travel & Vacation': ['Accommodation', 'Transportation', 'Food & Dining', 'Activities', 'Travel Insurance'],
        'Financial': ['Bank Fees', 'Investment', 'Savings', 'Loan Payment', 'Credit Card Payment', 'Insurance Premium'],
        'Personal': ['Haircut & Beauty', 'Clothing Care', 'Pet Care', 'Child Care'],
        'Other': ['Charity & Donations', 'Taxes', 'Legal Fees', 'Miscellaneous']
    }
    
    for main_category, subcategories in default_categories.items():
        # Create the main category
        if not Category.query.filter_by(name=main_category).first():
            category = Category(name=main_category)
            db.session.add(category)
            db.session.flush()  # Flush to get the ID
            
            # Create subcategories
            for subcategory_name in subcategories:
                if not Category.query.filter_by(name=subcategory_name).first():
                    subcategory = Category(name=subcategory_name, parent_id=category.id)
                    db.session.add(subcategory)
    
    db.session.commit()

def create_default_investment_types():
    """Creates default investment types."""
    main_types = [
        {
            'name': 'Securities',
            'code': 'securities',
            'icon': 'fas fa-chart-line',
            'color': '#3B82F6',
            'children': [
                {'name': 'Stocks', 'code': 'stocks', 'icon': 'fas fa-chart-line', 'color': '#3B82F6'},
                {'name': 'ETF', 'code': 'etf', 'icon': 'fas fa-chart-bar', 'color': '#8B5CF6'}
            ]
        },
        {
            'name': 'Crypto',
            'code': 'crypto',
            'icon': 'fab fa-bitcoin',
            'color': '#F59E0B',
            'children': [
                {'name': 'Bitcoin', 'code': 'btc', 'icon': 'fab fa-bitcoin', 'color': '#F59E0B'},
                {'name': 'Ethereum', 'code': 'eth', 'icon': 'fab fa-ethereum', 'color': '#6366F1'}
            ]
        },
        {
            'name': 'Metals',
            'code': 'metals',
            'icon': 'fas fa-coins',
            'color': '#FCD34D',
            'children': [
                {'name': 'Gold', 'code': 'gold', 'icon': 'fas fa-coins', 'color': '#FCD34D'},
                {'name': 'Silver', 'code': 'silver', 'icon': 'fas fa-medal', 'color': '#9CA3AF'}
            ]
        },
        {
            'name': 'Currency',
            'code': 'currency',
            'icon': 'fas fa-dollar-sign',
            'color': '#10B981',
            'children': [
                {'name': 'USD', 'code': 'usd', 'icon': 'fas fa-dollar-sign', 'color': '#10B981'},
                {'name': 'EUR', 'code': 'eur', 'icon': 'fas fa-euro-sign', 'color': '#3B82F6'}
            ]
        },
        {
            'name': 'Other',
            'code': 'other',
            'icon': 'fas fa-ellipsis-h',
            'color': '#6B7280',
            'children': [
                {'name': 'Real Estate', 'code': 'real_estate', 'icon': 'fas fa-home', 'color': '#EC4899'},
                {'name': 'Bonds', 'code': 'bonds', 'icon': 'fas fa-file-contract', 'color': '#059669'},
                {'name': 'Other', 'code': 'misc', 'icon': 'fas fa-question', 'color': '#6B7280'}
            ]
        }
    ]

    # Create main types and subtypes
    for main_type in main_types:
        children = main_type.pop('children', [])
        
        # Create main type
        if not InvestmentType.query.filter_by(code=main_type['code']).first():
            parent_type = InvestmentType(**main_type)
            db.session.add(parent_type)
            db.session.flush()  # Flush to get ID
            
            # Create subtypes
            for child in children:
                if not InvestmentType.query.filter_by(code=child['code']).first():
                    child_type = InvestmentType(**child, parent_id=parent_type.id)
                    db.session.add(child_type)

    db.session.commit()

def create_default_tags():
    """Creates default tags."""
    default_tags = [
        # Payment Method
        'Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'Mobile Payment',
        # Frequency
        'Recurring', 'One-time',
        # Planning
        'Planned', 'Unplanned',
        # Purpose
        'Personal', 'Business', 'Family', 'Investment',
        # Tax Related
        'Tax Deductible', 'Reimbursable'
    ]

    # Create tags
    for tag_name in default_tags:
        if not Tag.query.filter_by(name=tag_name).first():
            tag = Tag(name=tag_name)
            db.session.add(tag)

    db.session.commit()

def create_dummy_transactions(start_date, end_date):
    """Creates sample transactions within the specified date range."""
    # Get categories and tags
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # Sample transaction descriptions
    descriptions = [
        'Market shopping', 'Restaurant meal', 'Cinema ticket',
        'Rent payment', 'Electricity bill', 'Water bill',
        'Internet bill', 'Phone bill', 'Salary',
        'Freelance project', 'Gift', 'Holiday', 'Gym membership',
        'Book shopping', 'Clothing shopping', 'Public transport',
        'Taxi', 'Fuel', 'Health insurance', 'Doctor appointment'
    ]
    
    current_date = start_date
    while current_date <= end_date:
        # Create 1-3 transactions per day
        num_transactions = random.randint(1, 3)
        
        for _ in range(num_transactions):
            # Choose a random transaction type
            transaction_type = random.choice(['income', 'expense'])
            
            # Create a random amount based on the transaction type
            if transaction_type == 'income':
                amount = round(random.uniform(1000, 10000), 2)
            else:
                amount = round(random.uniform(50, 2000), 2)
            
            # Choose a random category and tags
            category = random.choice(categories)
            selected_tags = random.sample(tags, k=random.randint(0, 3))
            
            # Create the transaction
            transaction = CashflowTransaction(
                date=current_date,
                type=transaction_type,
                amount=amount,
                description=random.choice(descriptions),
                category_id=category.id,
                tags=selected_tags
            )
            
            db.session.add(transaction)
        
        current_date += timedelta(days=1)

def create_dummy_investments(start_date, end_date):
    """Creates sample investment transactions within the specified date range."""
    # Get investment types
    investment_types = InvestmentType.query.all()
    
    current_date = start_date
    while current_date <= end_date:
        # Create 1-2 investment transactions on the 1st of each month
        if current_date.day == 1:
            num_investments = random.randint(1, 2)
            for _ in range(num_investments):
                # Choose a random investment type
                investment_type = random.choice(investment_types)
                
                # Create investment quantity and prices
                quantity = round(random.uniform(1, 10), 2)
                price = round(random.uniform(100, 1000), 2)
                type = random.choice(['buy', 'sell'])
                
                # Create the investment transaction
                transaction = InvestmentTransaction(
                    investment_type_id=investment_type.id,
                    transaction_date=current_date,
                    transaction_type=type,
                    price=price,
                    quantity=quantity,
                    description=f'{investment_type.name} {type} transaction'
                )
                
                db.session.add(transaction)
        
        current_date += timedelta(days=1)
    
    db.session.commit()

def create_dummy_data():
    """Creates default categories, tags, investment types, and dummy transactions."""
    create_default_categories()
    create_default_tags()
    create_default_investment_types()
    
    start_date = datetime.now() - timedelta(days=90)
    end_date = datetime.now()
    
    create_dummy_transactions(start_date, end_date)
    create_dummy_investments(start_date, end_date)
    
    db.session.commit() 