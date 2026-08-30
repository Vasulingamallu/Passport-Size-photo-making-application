from app.extensions import db

class CountryRequirement(db.Model):
    __tablename__ = 'country_requirements'

    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    width_mm = db.Column(db.Float, nullable=False)
    height_mm = db.Column(db.Float, nullable=False)
    dpi = db.Column(db.Integer, default=300)
    background_color = db.Column(db.String(20), default='#FFFFFF')
    head_size_min = db.Column(db.Integer, default=50)
    head_size_max = db.Column(db.Integer, default=80)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'country_name': self.country_name,
            'country_code': self.country_code,
            'document_type': self.document_type,
            'width_mm': self.width_mm,
            'height_mm': self.height_mm,
            'dpi': self.dpi,
            'background_color': self.background_color,
            'head_size_min': self.head_size_min,
            'head_size_max': self.head_size_max,
            'notes': self.notes
        }
