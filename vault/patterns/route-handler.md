---
title: Route Handler Pattern
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
  - routes/cashflow.py
  - routes/category.py
---

# Route Handler Pattern

The standard pattern for Flask route handlers in track-finance. Every route follows this structure for consistency and safety.

## Blueprint Setup

Each domain has its own Blueprint with a url_prefix:

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash

blueprint_bp = Blueprint('domain', __name__, url_prefix='/domain')
```

Naming convention: `{feature}_bp` (e.g., `cashflow_bp`, `category_bp`).

## GET/POST Route Pattern

Combined GET/POST handlers for forms:

```python
@blueprint.route('/resource/add', methods=['GET', 'POST'])
def add_resource():
    if request.method == 'POST':
        try:
            # 1. Validate and parse input
            # 2. Create model instance
            db.session.add(obj)
            db.session.commit()
            flash('Added successfully.', 'success')
            return redirect(url_for('blueprint.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error: {e}")
            flash('An error occurred.', 'danger')
    # GET: render form
    return render_template('feature/form.html')
```

## Key Rules

1. **Always try/except with rollback** — Every POST handler wraps database operations in try/except. On failure: `db.session.rollback()`, `logger.error()`, `flash()` with error message.

2. **Input validation before DB** — Parse and validate `request.form` values (dates, amounts, enum fields like `income`/`expense`) before creating model instances. Return early with flash on invalid input.

3. **Use `db.get_or_404()`** — For edit/delete routes that take an ID parameter. Raises 404 automatically.

4. **Flash messages in English** — Categories: `success`, `danger`/`error`, `warning`, `info`.

5. **Redirect after POST** — Always `redirect(url_for(...))` after successful POST, never render template directly (PRG pattern).

6. **Logger before flash on errors** — `logger.error()` first for server logs, then `flash()` for user feedback.

## Edit Route Pattern

```python
@blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_resource(id):
    obj = db.get_or_404(Model, id)
    if request.method == 'POST':
        try:
            obj.field = request.form['field']
            db.session.commit()
            flash('Updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error: {e}')
            flash('An error occurred.', 'error')
        return redirect(url_for('blueprint.index'))
    return render_template('feature/form.html', obj=obj)
```

## Delete Route Pattern

```python
@blueprint.route('/delete/<int:id>', methods=['POST'])
def delete_resource(id):
    obj = db.get_or_404(Model, id)
    try:
        db.session.delete(obj)
        db.session.commit()
        flash('Deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error: {e}')
        flash('An error occurred.', 'error')
    return redirect(url_for('blueprint.index'))
```

**Delete protection:** For models with children (Category, InvestmentType), check for child records/transactions before allowing deletion.

## Filter/List Pattern

```python
@blueprint.route('/')
def index():
    query = Model.query
    # Apply filters from request.args
    if filter_param:
        query = query.filter(...)
    items = query.order_by(Model.date.desc()).all()
    return render_template('feature/index.html', items=items)
```

## Related

- [[cashflow]]
- [[model-definition]]
- [[template-structure]]
- [[2026-01-15-no-spa]]
