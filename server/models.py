from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = 'exercises'

    __table_args__ = (
        db.CheckConstraint('length(trim(name)) > 0', name='ck_exercise_name_not_blank'),
        db.CheckConstraint('length(trim(category)) > 0', name='ck_exercise_category_not_blank'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan'
    )
    workouts = association_proxy('workout_exercises', 'workout')

    @validates('name', 'category')
    def validate_not_blank(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{key} must be a non-empty string.')
        return value.strip()

    def __repr__(self):
        return f'<Exercise {self.id}: {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'

    __table_args__ = (
        db.CheckConstraint('duration_minutes > 0', name='ck_workout_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout', cascade='all, delete-orphan'
    )
    exercises = association_proxy('workout_exercises', 'exercise')

    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError('duration_minutes must be a positive integer.')
        return value

    @validates('notes')
    def validate_notes(self, key, value):
        if value is not None and len(value) > 500:
            raise ValueError('notes must be 500 characters or fewer.')
        return value

    def __repr__(self):
        return f'<Workout {self.id}: {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    __table_args__ = (
        db.UniqueConstraint('workout_id', 'exercise_id', name='uq_workout_exercise_pair'),
        db.CheckConstraint('reps IS NULL OR reps > 0', name='ck_we_reps_positive'),
        db.CheckConstraint('sets IS NULL OR sets > 0', name='ck_we_sets_positive'),
        db.CheckConstraint(
            'duration_seconds IS NULL OR duration_seconds > 0',
            name='ck_we_duration_positive',
        ),
        db.CheckConstraint(
            'reps IS NOT NULL OR duration_seconds IS NOT NULL',
            name='ck_we_reps_or_duration',
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
cat > server/app.py << 'EOF'
from flask import Flask, make_response
from flask_migrate import Migrate

from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

# Define Routes here

if __name__ == '__main__':
    app.run(port=5555, debug=True)
