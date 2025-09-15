from src.models.user import db
from datetime import datetime
from sqlalchemy import func

class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500), nullable=False)
    thumbnail_path = db.Column(db.String(500))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)  # in bytes
    duration = db.Column(db.String(20))  # e.g., "2h 30m"
    
    # New fields for enhanced features
    year = db.Column(db.Integer, nullable=True)
    genre = db.Column(db.String(100), nullable=True)  # Action, Comedy, Drama, etc.
    category = db.Column(db.String(50), nullable=True)  # Bollywood, Hollywood, etc.
    language = db.Column(db.String(50), nullable=True)  # Hindi, English, etc.
    quality = db.Column(db.String(20), nullable=True)  # 720p, 1080p, etc.
    imdb_rating = db.Column(db.Float, nullable=True)
    views = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Movie {self.title}>'
    
    def get_average_rating(self):
        """Get average user rating for this movie"""
        from src.models.user import UserRating
        avg_rating = db.session.query(func.avg(UserRating.rating)).filter_by(movie_id=self.id).scalar()
        return round(avg_rating, 1) if avg_rating else 0
    
    def get_rating_count(self):
        """Get total number of ratings for this movie"""
        from src.models.user import UserRating
        return UserRating.query.filter_by(movie_id=self.id).count()
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        db.session.commit()
    
    def increment_downloads(self):
        """Increment download count"""
        self.downloads += 1
        db.session.commit()
    
    def to_dict(self, include_stats=False):
        """Convert movie to dictionary"""
        movie_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'thumbnail_path': self.thumbnail_path,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'file_size': self.file_size,
            'duration': self.duration,
            'year': self.year,
            'genre': self.genre,
            'category': self.category,
            'language': self.language,
            'quality': self.quality,
            'imdb_rating': self.imdb_rating,
            'views': self.views,
            'downloads': self.downloads,
            'is_featured': self.is_featured
        }
        
        if include_stats:
            movie_dict.update({
                'average_rating': self.get_average_rating(),
                'rating_count': self.get_rating_count()
            })
        
        return movie_dict

