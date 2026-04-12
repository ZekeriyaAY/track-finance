from models import db

# Many-to-many association table for CategorizationRule <-> Tag
categorization_rule_tags = db.Table('categorization_rule_tags',
    db.Column('categorization_rule_id', db.Integer, db.ForeignKey('categorization_rule.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class CategorizationRule(db.Model):
    __tablename__ = 'categorization_rule'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Condition
    field = db.Column(db.String(20), nullable=False, default='description')
    operator = db.Column(db.String(20), nullable=False)  # contains, equals, starts_with, ends_with
    value = db.Column(db.String(255), nullable=False)

    # Actions
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    type_override = db.Column(db.String(10), nullable=True)  # income, expense, or NULL

    # Relationships
    category = db.relationship('Category', backref='categorization_rules')
    tags = db.relationship('Tag', secondary='categorization_rule_tags', backref='categorization_rules')

    @staticmethod
    def normalize(text):
        """Normalize text to lowercase with Turkish character support.

        Maps all I-variants (I, İ, ı) to 'i' so that MIGROS, Migros, MİGROS
        all match consistently. Other Turkish chars handled by standard lower().
        """
        result = text.replace('İ', 'i').replace('ı', 'i').replace('I', 'i')
        return result.lower()

    def matches(self, description):
        """Match description against the rule. Value is already normalized in DB."""
        if not description:
            return False
        desc = self.normalize(description)
        val = self.value  # already normalized at save time
        if self.operator == 'contains':
            return val in desc
        elif self.operator == 'equals':
            return desc == val
        elif self.operator == 'starts_with':
            return desc.startswith(val)
        elif self.operator == 'ends_with':
            return desc.endswith(val)
        return False
