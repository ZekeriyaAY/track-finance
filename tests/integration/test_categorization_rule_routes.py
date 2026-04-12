"""Integration tests for categorization rule routes."""
import pytest
from tests.conftest import get_csrf_token
from models.categorization_rule import CategorizationRule
from models.category import Category
from models.tag import Tag


@pytest.mark.integration
class TestCategorizationRuleIndex:

    def test_index_requires_login(self, client):
        response = client.get('/rules/')
        assert response.status_code in (302, 308)

    def test_index_empty(self, auth_client):
        response = auth_client.get('/rules/')
        assert response.status_code == 200
        assert b'No rules defined yet' in response.data

    def test_index_shows_rules(self, auth_client, sample_rule):
        response = auth_client.get('/rules/')
        assert response.status_code == 200
        assert b'Test Rule' in response.data
        assert b'migros' in response.data

    def test_index_ordered_by_priority(self, auth_client, db, sample_subcategory):
        rule1 = CategorizationRule(
            name='Second Rule', priority=1, operator='contains',
            value='B', category_id=sample_subcategory.id,
        )
        rule2 = CategorizationRule(
            name='First Rule', priority=0, operator='contains',
            value='A', category_id=sample_subcategory.id,
        )
        db.session.add_all([rule1, rule2])
        db.session.commit()

        response = auth_client.get('/rules/')
        data = response.data.decode()
        assert data.index('First Rule') < data.index('Second Rule')


@pytest.mark.integration
class TestCategorizationRuleAdd:

    def test_add_form_renders(self, auth_client, sample_category):
        response = auth_client.get('/rules/add')
        assert response.status_code == 200
        assert b'Add Rule' in response.data

    def test_add_rule(self, auth_client, db, sample_subcategory):
        csrf = get_csrf_token(auth_client, '/rules/add')
        response = auth_client.post('/rules/add', data={
            'csrf_token': csrf,
            'name': 'New Rule',
            'operator': 'contains',
            'value': 'MARKET',
            'category_id': sample_subcategory.id,
            'is_active': '1',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Rule added successfully' in response.data

        with auth_client.application.app_context():
            rule = CategorizationRule.query.filter_by(name='New Rule').first()
            assert rule is not None
            assert rule.operator == 'contains'
            assert rule.value == 'market'  # normalized to lowercase

    def test_add_rule_with_tags(self, auth_client, db, sample_subcategory, sample_tag):
        csrf = get_csrf_token(auth_client, '/rules/add')
        response = auth_client.post('/rules/add', data={
            'csrf_token': csrf,
            'name': 'Tagged Rule',
            'operator': 'equals',
            'value': 'Netflix',
            'category_id': sample_subcategory.id,
            'tags': [str(sample_tag.id)],
            'is_active': '1',
        }, follow_redirects=True)
        assert response.status_code == 200

        with auth_client.application.app_context():
            rule = CategorizationRule.query.filter_by(name='Tagged Rule').first()
            assert len(rule.tags) == 1

    def test_add_rule_with_type_override(self, auth_client, db, sample_subcategory):
        csrf = get_csrf_token(auth_client, '/rules/add')
        response = auth_client.post('/rules/add', data={
            'csrf_token': csrf,
            'name': 'Income Rule',
            'operator': 'contains',
            'value': 'MAAS',
            'category_id': sample_subcategory.id,
            'type_override': 'income',
            'is_active': '1',
        }, follow_redirects=True)
        assert response.status_code == 200

        with auth_client.application.app_context():
            rule = CategorizationRule.query.filter_by(name='Income Rule').first()
            assert rule.type_override == 'income'

    def test_add_rule_missing_fields(self, auth_client, db, sample_subcategory):
        csrf = get_csrf_token(auth_client, '/rules/add')
        response = auth_client.post('/rules/add', data={
            'csrf_token': csrf,
            'name': '',
            'operator': 'contains',
            'value': '',
            'category_id': sample_subcategory.id,
        }, follow_redirects=True)
        assert b'Please fill in all required fields' in response.data

    def test_add_rule_invalid_operator(self, auth_client, db, sample_subcategory):
        csrf = get_csrf_token(auth_client, '/rules/add')
        response = auth_client.post('/rules/add', data={
            'csrf_token': csrf,
            'name': 'Bad Rule',
            'operator': 'regex',
            'value': 'test',
            'category_id': sample_subcategory.id,
        }, follow_redirects=True)
        assert b'Please fill in all required fields' in response.data

    def test_add_requires_csrf(self, auth_client, db, sample_subcategory):
        response = auth_client.post('/rules/add', data={
            'name': 'No CSRF',
            'operator': 'contains',
            'value': 'test',
            'category_id': sample_subcategory.id,
        })
        assert response.status_code == 400

    def test_priority_auto_increments(self, auth_client, db, sample_subcategory):
        csrf = get_csrf_token(auth_client, '/rules/add')
        auth_client.post('/rules/add', data={
            'csrf_token': csrf,
            'name': 'Rule 1', 'operator': 'contains', 'value': 'A',
            'category_id': sample_subcategory.id, 'is_active': '1',
        })
        csrf = get_csrf_token(auth_client, '/rules/add')
        auth_client.post('/rules/add', data={
            'csrf_token': csrf,
            'name': 'Rule 2', 'operator': 'contains', 'value': 'B',
            'category_id': sample_subcategory.id, 'is_active': '1',
        })

        with auth_client.application.app_context():
            r1 = CategorizationRule.query.filter_by(name='Rule 1').first()
            r2 = CategorizationRule.query.filter_by(name='Rule 2').first()
            assert r2.priority > r1.priority


@pytest.mark.integration
class TestCategorizationRuleEdit:

    def test_edit_form_renders(self, auth_client, sample_rule):
        response = auth_client.get(f'/rules/edit/{sample_rule.id}')
        assert response.status_code == 200
        assert b'Edit Rule' in response.data
        assert b'migros' in response.data

    def test_edit_rule(self, auth_client, db, sample_rule):
        csrf = get_csrf_token(auth_client, f'/rules/edit/{sample_rule.id}')
        response = auth_client.post(f'/rules/edit/{sample_rule.id}', data={
            'csrf_token': csrf,
            'name': 'Updated Rule',
            'operator': 'equals',
            'value': 'BIM',
            'category_id': sample_rule.category_id,
            'is_active': '1',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Rule updated successfully' in response.data

        with auth_client.application.app_context():
            rule = db.session.get(CategorizationRule, sample_rule.id)
            assert rule.name == 'Updated Rule'
            assert rule.operator == 'equals'
            assert rule.value == 'bim'  # normalized to lowercase

    def test_edit_nonexistent_rule(self, auth_client):
        response = auth_client.get('/rules/edit/99999')
        # App 404 handler redirects to cashflow index
        assert response.status_code == 302


@pytest.mark.integration
class TestCategorizationRuleDelete:

    def test_delete_rule(self, auth_client, db, sample_rule):
        csrf = get_csrf_token(auth_client, '/rules/')
        response = auth_client.post(f'/rules/delete/{sample_rule.id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Rule deleted successfully' in response.data

        with auth_client.application.app_context():
            assert db.session.get(CategorizationRule, sample_rule.id) is None

    def test_delete_requires_csrf(self, auth_client, sample_rule):
        response = auth_client.post(f'/rules/delete/{sample_rule.id}', data={})
        assert response.status_code == 400

    def test_delete_nonexistent_rule(self, auth_client):
        csrf = get_csrf_token(auth_client, '/rules/add')
        response = auth_client.post('/rules/delete/99999', data={
            'csrf_token': csrf,
        })
        # App 404 handler redirects to cashflow index
        assert response.status_code == 302


@pytest.mark.integration
class TestCategorizationRuleReorder:

    def test_reorder_rules(self, auth_client, db, sample_subcategory):
        rule1 = CategorizationRule(
            name='Rule A', priority=0, operator='contains',
            value='A', category_id=sample_subcategory.id,
        )
        rule2 = CategorizationRule(
            name='Rule B', priority=1, operator='contains',
            value='B', category_id=sample_subcategory.id,
        )
        db.session.add_all([rule1, rule2])
        db.session.commit()

        csrf = get_csrf_token(auth_client, '/rules/')
        response = auth_client.post('/rules/reorder',
            json={'rule_ids': [rule2.id, rule1.id]},
            headers={'X-CSRFToken': csrf},
        )
        assert response.status_code == 200

        with auth_client.application.app_context():
            r1 = db.session.get(CategorizationRule, rule1.id)
            r2 = db.session.get(CategorizationRule, rule2.id)
            assert r2.priority < r1.priority

    def test_reorder_invalid_request(self, auth_client):
        csrf = get_csrf_token(auth_client, '/rules/')
        response = auth_client.post('/rules/reorder',
            json={},
            headers={'X-CSRFToken': csrf},
        )
        assert response.status_code == 400
