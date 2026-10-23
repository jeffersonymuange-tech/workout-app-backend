from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutExerciseSchema, WorkoutSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workout_exercises',))
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
workout_exercise_schema = WorkoutExerciseSchema()


def error(message, status):
    return make_response(jsonify({'error': message}), status)


def save(obj):
    """Add obj and commit. Returns an error response on failure, else None."""
    try:
        db.session.add(obj)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return error(str(e), 400)
    except IntegrityError:
        db.session.rollback()
        return error('Database constraint violated (duplicate or invalid data).', 409)
    return None


# ---------- Workouts ----------

@app.route('/workouts', methods=['GET'])
def get_workouts():
    return make_response(jsonify(workouts_schema.dump(Workout.query.all())), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error('Workout not found.', 404)
    return make_response(jsonify(workout_schema.dump(workout)), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    try:
        data = workout_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)

    try:
        workout = Workout(**data)
    except ValueError as e:
        return error(str(e), 400)

    failure = save(workout)
    if failure:
        return failure
    return make_response(jsonify(workout_schema.dump(workout)), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error('Workout not found.', 404)
    db.session.delete(workout)  # cascade removes its WorkoutExercises
    db.session.commit()
    return make_response('', 204)


# ---------- Exercises ----------

@app.route('/exercises', methods=['GET'])
def get_exercises():
    return make_response(jsonify(exercises_schema.dump(Exercise.query.all())), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error('Exercise not found.', 404)
    return make_response(jsonify(exercise_schema.dump(exercise)), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)

    try:
        exercise = Exercise(**data)
    except ValueError as e:
        return error(str(e), 400)

    failure = save(exercise)
    if failure:
        return failure
    return make_response(jsonify(exercise_schema.dump(exercise)), 201)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error('Exercise not found.', 404)
    db.session.delete(exercise)  # cascade removes its WorkoutExercises
    db.session.commit()
    return make_response('', 204)


# ---------- Workout <-> Exercise ----------

@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST'],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error('Workout not found.', 404)
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error('Exercise not found.', 404)

    try:
        data = workout_exercise_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)

    try:
        link = WorkoutExercise(workout=workout, exercise=exercise, **data)
    except ValueError as e:
        db.session.rollback()
        return error(str(e), 400)

    failure = save(link)
    if failure:
        return failure
    return make_response(jsonify(workout_exercise_schema.dump(link)), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
