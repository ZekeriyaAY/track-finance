"""Unit tests for the CategorizationRule model."""
import pytest
from models.categorization_rule import CategorizationRule
from models.tag import Tag


@pytest.mark.unit
class TestCategorizationRuleModel:

    def test_create_rule(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='Grocery Rule',
            priority=0,
            field='description',
            operator='contains',
            value='MIGROS',
            category_id=sample_subcategory.id,
        )
        db.session.add(rule)
        db.session.commit()

        fetched = db.session.get(CategorizationRule, rule.id)
        assert fetched.name == 'Grocery Rule'
        assert fetched.priority == 0
        assert fetched.is_active is True
        assert fetched.field == 'description'
        assert fetched.operator == 'contains'
        assert fetched.value == 'MIGROS'
        assert fetched.category_id == sample_subcategory.id
        assert fetched.type_override is None

    def test_default_is_active(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='Rule', operator='contains', value='test',
            category_id=sample_subcategory.id,
        )
        db.session.add(rule)
        db.session.commit()
        assert rule.is_active is True

    def test_rule_with_type_override(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='Income Rule', operator='contains', value='MAAS',
            category_id=sample_subcategory.id, type_override='income',
        )
        db.session.add(rule)
        db.session.commit()
        assert rule.type_override == 'income'

    def test_rule_with_tags(self, app, db, sample_subcategory, sample_tag):
        tag2 = Tag(name='Second Tag')
        db.session.add(tag2)
        db.session.flush()

        rule = CategorizationRule(
            name='Tagged Rule', operator='contains', value='test',
            category_id=sample_subcategory.id, tags=[sample_tag, tag2],
        )
        db.session.add(rule)
        db.session.commit()
        assert len(rule.tags) == 2

    def test_category_relationship(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='Rule', operator='contains', value='test',
            category_id=sample_subcategory.id,
        )
        db.session.add(rule)
        db.session.commit()
        assert rule.category.name == 'Test Subcategory'


@pytest.mark.unit
class TestCategorizationRuleMatching:

    def test_contains_match(self, app, db, sample_subcategory):
        """Value is pre-normalized (lowercase) in DB."""
        rule = CategorizationRule(
            name='R', operator='contains', value='migros',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('MIGROS MARKET ALISVERISI') is True
        assert rule.matches('Migros Market') is True

    def test_contains_no_match(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='contains', value='migros',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('BIM MARKET') is False

    def test_equals_match(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='equals', value='netflix',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('NETFLIX') is True
        assert rule.matches('netflix') is True
        assert rule.matches('Netflix') is True

    def test_equals_no_match_substring(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='equals', value='netflix',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('Netflix Payment') is False

    def test_starts_with_match(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='starts_with', value='havale',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('HAVALE - Ali Veli') is True

    def test_starts_with_no_match(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='starts_with', value='havale',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('EFT HAVALE') is False

    def test_ends_with_match(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='ends_with', value='a.ş.',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('TURKCELL İLETİŞİM A.Ş.') is True

    def test_ends_with_no_match(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='ends_with', value='a.ş.',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('A.Ş. TURKCELL') is False

    def test_case_insensitive(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='contains', value='maaş',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('MAAŞ ÖDEMESİ') is True
        assert rule.matches('maaş ödemesi') is True

    def test_turkish_i_uppercase(self, app, db, sample_subcategory):
        """Turkish İ in description should match i in value."""
        rule = CategorizationRule(
            name='R', operator='contains', value='çiçek',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('ÇİÇEK SEPETİ') is True

    def test_turkish_i_dotless(self, app, db, sample_subcategory):
        """Turkish ı in description normalized to i, matching value."""
        rule = CategorizationRule(
            name='R', operator='contains', value='kira',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('KIRA ÖDEMESİ') is True
        assert rule.matches('kıra ödemesi') is True

    def test_normalize_static_method(self, app, db, sample_subcategory):
        """normalize() used at save time to lowercase value."""
        assert CategorizationRule.normalize('İŞLEM') == 'işlem'
        assert CategorizationRule.normalize('MIGROS') == 'migros'
        assert CategorizationRule.normalize('Kıra') == 'kira'

    def test_empty_description(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='contains', value='test',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('') is False

    def test_none_description(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='contains', value='test',
            category_id=sample_subcategory.id,
        )
        assert rule.matches(None) is False

    def test_invalid_operator(self, app, db, sample_subcategory):
        rule = CategorizationRule(
            name='R', operator='regex', value='test',
            category_id=sample_subcategory.id,
        )
        assert rule.matches('test') is False
