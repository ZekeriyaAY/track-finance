"""Integration tests for tag routes (/tags)."""
import pytest
from tests.conftest import get_csrf_token
from models.tag import Tag


pytestmark = pytest.mark.integration


class TestTagIndexRoute:
    """Tests for GET /tags/."""

    def test_index_renders(self, auth_client):
        """GET /tags/ returns 200 with tag list page."""
        response = auth_client.get('/tags/')
        assert response.status_code == 200

    def test_index_shows_tags(self, auth_client, sample_tag):
        """GET /tags/ shows existing tags."""
        response = auth_client.get('/tags/')
        assert response.status_code == 200
        assert b'Test Tag' in response.data

    def test_index_shows_tags_sorted_by_name(self, auth_client, app, db):
        """GET /tags/ shows tags sorted by name."""
        with app.app_context():
            db.session.add(Tag(name='Zebra Tag'))
            db.session.add(Tag(name='Alpha Tag'))
            db.session.commit()

        response = auth_client.get('/tags/')
        assert response.status_code == 200
        data = response.data.decode()
        alpha_pos = data.find('Alpha Tag')
        zebra_pos = data.find('Zebra Tag')
        assert alpha_pos < zebra_pos

    def test_index_requires_auth(self, client, admin_user):
        """GET /tags/ redirects to login when not authenticated."""
        response = client.get('/tags/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')


class TestAddTagRoute:
    """Tests for GET/POST /tags/add."""

    def test_add_form_renders(self, auth_client):
        """GET /tags/add returns the add tag form."""
        response = auth_client.get('/tags/add')
        assert response.status_code == 200
        assert b'csrf_token' in response.data

    def test_add_tag_success(self, auth_client, app, db):
        """POST /tags/add creates a new tag."""
        csrf = get_csrf_token(auth_client, '/tags/add')
        response = auth_client.post('/tags/add', data={
            'name': 'New Tag',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Tag added successfully' in response.data

        with app.app_context():
            tag = Tag.query.filter_by(name='New Tag').first()
            assert tag is not None

    def test_add_duplicate_tag(self, auth_client, sample_tag):
        """POST /tags/add with duplicate name shows error."""
        csrf = get_csrf_token(auth_client, '/tags/add')
        response = auth_client.post('/tags/add', data={
            'name': 'Test Tag',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data

    def test_add_tag_with_spaces_in_name(self, auth_client, app, db):
        """POST /tags/add with spaces in name creates tag successfully."""
        csrf = get_csrf_token(auth_client, '/tags/add')
        response = auth_client.post('/tags/add', data={
            'name': 'Tag With Spaces',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Tag added successfully' in response.data

    def test_add_tag_redirects_to_index(self, auth_client, app, db):
        """POST /tags/add redirects to tag index after creation."""
        csrf = get_csrf_token(auth_client, '/tags/add')
        response = auth_client.post('/tags/add', data={
            'name': 'Redirect Tag',
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/tags/' in response.headers.get('Location', '')


class TestEditTagRoute:
    """Tests for GET/POST /tags/edit/<id>."""

    def test_edit_form_renders(self, auth_client, sample_tag):
        """GET /tags/edit/<id> returns the edit form with pre-filled data."""
        response = auth_client.get(f'/tags/edit/{sample_tag.id}')
        assert response.status_code == 200
        assert b'Test Tag' in response.data
        assert b'csrf_token' in response.data

    def test_edit_tag_success(self, auth_client, app, db, sample_tag):
        """POST /tags/edit/<id> updates the tag name."""
        csrf = get_csrf_token(auth_client, f'/tags/edit/{sample_tag.id}')
        response = auth_client.post(f'/tags/edit/{sample_tag.id}', data={
            'name': 'Updated Tag',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Tag updated successfully' in response.data

        with app.app_context():
            tag = Tag.query.get(sample_tag.id)
            assert tag.name == 'Updated Tag'

    def test_edit_tag_duplicate_name(self, auth_client, app, db, sample_tag):
        """POST /tags/edit/<id> with duplicate name shows error."""
        with app.app_context():
            other_tag = Tag(name='Other Tag')
            db.session.add(other_tag)
            db.session.commit()
            other_id = other_tag.id

        csrf = get_csrf_token(auth_client, f'/tags/edit/{other_id}')
        response = auth_client.post(f'/tags/edit/{other_id}', data={
            'name': 'Test Tag',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data

    def test_edit_tag_same_name_no_conflict(self, auth_client, sample_tag):
        """POST /tags/edit/<id> keeping same name does not trigger duplicate error."""
        csrf = get_csrf_token(auth_client, f'/tags/edit/{sample_tag.id}')
        response = auth_client.post(f'/tags/edit/{sample_tag.id}', data={
            'name': 'Test Tag',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Tag updated successfully' in response.data

    def test_edit_nonexistent_tag(self, auth_client):
        """GET /tags/edit/99999 for nonexistent ID redirects (404 handler)."""
        response = auth_client.get('/tags/edit/99999', follow_redirects=False)
        assert response.status_code == 302

    def test_edit_tag_redirects_to_index(self, auth_client, sample_tag):
        """POST /tags/edit/<id> redirects to tag index after update."""
        csrf = get_csrf_token(auth_client, f'/tags/edit/{sample_tag.id}')
        response = auth_client.post(f'/tags/edit/{sample_tag.id}', data={
            'name': 'Renamed Tag',
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/tags/' in response.headers.get('Location', '')


class TestDeleteTagRoute:
    """Tests for POST /tags/delete/<id>."""

    def test_delete_tag_success(self, auth_client, app, db, sample_tag):
        """POST /tags/delete/<id> removes a tag with no transactions."""
        csrf = get_csrf_token(auth_client, '/tags/')
        tag_id = sample_tag.id
        response = auth_client.post(f'/tags/delete/{tag_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Tag deleted successfully' in response.data

        with app.app_context():
            tag = Tag.query.get(tag_id)
            assert tag is None

    def test_delete_tag_with_transactions(self, auth_client, app, db, sample_tag, sample_transaction):
        """POST /tags/delete/<id> with transactions shows protection error."""
        csrf = get_csrf_token(auth_client, '/tags/')
        response = auth_client.post(f'/tags/delete/{sample_tag.id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'associated transactions' in response.data

        # Tag should still exist
        with app.app_context():
            tag = Tag.query.get(sample_tag.id)
            assert tag is not None

    def test_delete_nonexistent_tag(self, auth_client):
        """POST /tags/delete/99999 for nonexistent ID redirects (404 handler)."""
        csrf = get_csrf_token(auth_client, '/tags/add')
        response = auth_client.post('/tags/delete/99999', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302

    def test_delete_tag_redirects_to_index(self, auth_client, app, db):
        """POST /tags/delete/<id> redirects to tag index."""
        with app.app_context():
            tag = Tag(name='Temp Tag')
            db.session.add(tag)
            db.session.commit()
            tag_id = tag.id

        csrf = get_csrf_token(auth_client, '/tags/')
        response = auth_client.post(f'/tags/delete/{tag_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/tags/' in response.headers.get('Location', '')
