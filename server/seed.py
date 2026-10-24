
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Clearing existing data...')
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Creating exercises...')
    squat = Exercise(name='Squat', category='Strength', equipment_needed=True)
    pushup = Exercise(name='Push-up', category='Strength', equipment_needed=False)
    plank = Exercise(name='Plank', category='Core', equipment_needed=False)
    run = Exercise(name='Treadmill Run', category='Cardio', equipment_needed=True)
    db.session.add_all([squat, pushup, plank, run])

    print('Creating workouts...')
    w1 = Workout(date=date(2026, 10, 19), duration_minutes=45, notes='Upper and lower body day')
    w2 = Workout(date=date(2026, 10, 21), duration_minutes=30, notes='Cardio and core')
    db.session.add_all([w1, w2])
    db.session.commit()

    print('Linking exercises to workouts...')
    db.session.add_all([
        WorkoutExercise(workout=w1, exercise=squat, reps=10, sets=4),
        WorkoutExercise(workout=w1, exercise=pushup, reps=15, sets=3),
        WorkoutExercise(workout=w1, exercise=plank, duration_seconds=60, sets=3),
        WorkoutExercise(workout=w2, exercise=run, duration_seconds=1200),
        WorkoutExercise(workout=w2, exercise=plank, duration_seconds=90, sets=2),
    ])
    db.session.commit()
    print('Done seeding!')
