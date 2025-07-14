from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import _
from datetime import datetime
from models.__init__ import db
from models.cashflow import CashflowTransaction
from models.category import Category
from models.tag import Tag
import logging
import os
import tempfile
from werkzeug.utils import secure_filename
from utils.bank_configs import get_bank_config
from utils.excel_processor import process_excel_data, ExcelImportError

logger = logging.getLogger(__name__)

cashflow_bp = Blueprint('cashflow', __name__, url_prefix='/cashflow')

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cashflow_bp.route('/')
def index():
    transactions = CashflowTransaction.query.order_by(CashflowTransaction.date.desc()).all()
    return render_template('cashflow/index.html', transactions=transactions)

@cashflow_bp.route('/add', methods=['GET', 'POST'])
def add_cashflow():
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        amount = float(request.form['amount'])
        type = request.form['type']
        category_id = int(request.form['category_id'])
        tag_ids = request.form.getlist('tags')
        description = request.form['description']

        try:
            transaction = CashflowTransaction(
                date=date,
                amount=amount,
                type=type,
                category_id=category_id,
                description=description
            )
            if tag_ids:
                tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                transaction.tags = tags
            db.session.add(transaction)
            db.session.commit()
            flash(_('Transaction added successfully!'), 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding transaction: {str(e)}')
            flash(_('An error occurred while adding the transaction.'), 'error')
        return redirect(url_for('cashflow.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('cashflow/form.html', categories=categories, tags=tags, today=today)

@cashflow_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_cashflow(id):
    transaction = CashflowTransaction.query.get_or_404(id)
    if request.method == 'POST':
        try:
            transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            transaction.amount = float(request.form['amount'])
            transaction.type = request.form['type']
            transaction.category_id = int(request.form['category_id'])
            transaction.description = request.form['description']

            tag_ids = request.form.getlist('tags')
            transaction.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
            db.session.commit()
            flash(_('Transaction updated successfully!'), 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating transaction: {str(e)}')
            flash(_('An error occurred while updating the transaction.'), 'error')
        return redirect(url_for('cashflow.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    return render_template('cashflow/form.html', transaction=transaction, categories=categories, tags=tags)

@cashflow_bp.route('/delete/<int:id>', methods=['POST'])
def delete_cashflow(id):
    transaction = CashflowTransaction.query.get_or_404(id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash(_('Transaction deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting transaction: {str(e)}')
        flash(_('An error occurred while deleting the transaction.'), 'error')
    return redirect(url_for('cashflow.index'))

@cashflow_bp.route('/import', methods=['GET', 'POST'])
def import_excel():
    """Excel dosyası ile transaction import etme"""
    
    if request.method == 'GET':
        return render_template('cashflow/import.html')
    
    try:
        logger.info(f"Import request received. Form data: {dict(request.form)}")
        
        # import_excel butonuna basıldıysa direkt import et
        if 'import_excel' in request.form:
            logger.info("Direct import request")
        
        # Dosya kontrolü
        if 'excel_file' not in request.files:
            logger.warning("No excel_file in request.files")
            flash(_('Lütfen bir Excel dosyası seçin.'), 'error')
            return render_template('cashflow/import.html')
        
        file = request.files['excel_file']
        logger.info(f"File received: {file.filename}")
        
        if file.filename == '':
            logger.warning("Empty filename")
            flash(_('Lütfen bir Excel dosyası seçin.'), 'error')
            return render_template('cashflow/import.html')
        
        if not allowed_file(file.filename):
            logger.warning(f"File type not allowed: {file.filename}")
            flash(_('Sadece Excel dosyaları (.xlsx, .xls, .csv) desteklenmektedir.'), 'error')
            return render_template('cashflow/import.html')
        
        # Banka seçimi kontrolü
        bank_code = request.form.get('bank_code')
        if not bank_code:
            flash(_('Lütfen bir banka seçin.'), 'error')
            return render_template('cashflow/import.html')
        
        logger.info(f"Selected bank: {bank_code}")
        
        # Geçici dosya oluştur
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        logger.info(f"File saved to: {temp_path}")
        
        try:
            # Excel'i direkt işle
            logger.info("Processing Excel data...")
            result = process_excel_data(temp_path, bank_code)
            logger.info(f"Processing result: {result}")
            
            # Transaction'ları veritabanına kaydet
            saved_count = 0
            
            # Default category oluştur/bul (Import)
            import_category = Category.query.filter_by(name='Import').first()
            if not import_category:
                import_category = Category(name='Import')
                db.session.add(import_category)
                db.session.flush()  # ID'yi almak için
            
            # Seçilen banka için tag oluştur/bul
            bank_config = get_bank_config(bank_code)
            bank_tag = Tag.query.filter_by(name=bank_config['name']).first()
            if not bank_tag:
                bank_tag = Tag(name=bank_config['name'])
                db.session.add(bank_tag)
                db.session.flush()  # ID'yi almak için
            
            for transaction_data in result['transactions']:
                try:
                    transaction = CashflowTransaction(
                        date=transaction_data['date'],
                        amount=abs(transaction_data['amount']),  # Amount her zaman pozitif
                        type=transaction_data['type'],  # Excel processor'dan gelecek
                        category_id=import_category.id,
                        description=transaction_data['description'],
                        tags = [bank_tag]
                    )
                    
                    db.session.add(transaction)
                    saved_count += 1
                    logger.debug(f"Added transaction: {transaction_data['description']} - {transaction_data['amount']}")
                    
                except Exception as e:
                    logger.error(f"Transaction kaydetme hatası: {str(e)}")
                    continue
            
            db.session.commit()
            logger.info(f"Committed {saved_count} transactions to database")
            
            # Başarı mesajı
            success_msg = _(f'{saved_count} transaction başarıyla import edildi.')
            if result.get('failed', 0) > 0:
                success_msg += _(f' {result["failed"]} transaction başarısız.')
            flash(success_msg, 'success')
            
            # Hata varsa göster
            if result.get('errors'):
                error_details = []
                for error in result['errors'][:5]:  # İlk 5 hatayı göster
                    error_details.append(f"Satır {error['row']}: {error['error']}")
                flash(_('Hatalar: ') + '; '.join(error_details), 'warning')
            
        finally:
            # Geçici dosyayı sil
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Removed temp file: {temp_path}")
        
        return redirect(url_for('cashflow.index'))
    
    except ExcelImportError as e:
        logger.error(f"ExcelImportError: {str(e)}")
        flash(_(f'Excel import hatası: {str(e)}'), 'error')
    except Exception as e:
        logger.error(f'Import hatası: {str(e)}', exc_info=True)
        flash(_('Beklenmeyen bir hata oluştu.'), 'error')
    
    return render_template('cashflow/import.html')

