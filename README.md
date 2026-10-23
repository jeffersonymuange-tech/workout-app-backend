# Workout Tracker API

A Flask backend API for a workout tracking app used by personal trainers. It tracks workouts and the reusable exercises attached to them, including sets, reps or duration for each exercise in a workout.

Built with Flask, Flask-SQLAlchemy, Flask-Migrate and Marshmallow.

## Installation

```bash
git clone <your-repo-url>
cd workout-app-backend
pipenv install
pipenv shell
cd server
export FLASK_APP=app.py
flask db init
flask db migrate -m "Create tables"
flask db upgrade head
python seed.py
```

If a `migrations/` folder already exists, skip `flask db init`.

## Running

```bash
cd server
flask run --port 5555
```

The API runs at `http://localhost:5555`.

## Data model

- **Exercise**: name, category, equipment_needed
- **Workout**: date, duration_minutes, notes
- **WorkoutExercise** (join table): workout_id, exercise_id, reps, sets, duration_seconds

A workout has many exercises through WorkoutExercises, and an exercise has many workouts through WorkoutExercises.

## Validations

- **Table constraints:** unique exercise names, non-blank name/category, positive duration/reps/sets, unique exercise per workout, reps or duration required.
- **Model validations:** non-blank exercise fields, positive workout duration, notes max 500 characters, positive reps/sets/duration.
- **Schema validations:** required fields, length limits, duration range (1-600), positive reps/sets/duration, reps or duration_seconds required.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Show a workout with its exercises, including reps/sets/duration |
| POST | `/workouts` | Create a workout (`date`, `duration_minutes`, optional `notes`) |
| DELETE | `/workouts/<id>` | Delete a workout and its workout exercises |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show an exercise with its associated workouts |
| POST | `/exercises` | Create an exercise (`name`, `category`, optional `equipment_needed`) |
| DELETE | `/exercises/<id>` | Delete an exercise and its workout exercises |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout (`reps` and/or `duration_seconds`, optional `sets`) |

Error responses: `400` for validation errors, `404` when a record is not found, `409` for database constraint violations (such as a duplicate exercise name).

## Example requests

```bash
curl -X POST localhost:5555/exercises -H "Content-Type: application/json" \
  -d '{"name": "Lunge", "category": "Strength", "equipment_needed": false}'

curl -X POST localhost:5555/workouts/1/exercises/4/workout_exercises \
  -H "Content-Type: application/json" -d '{"reps": 12, "sets": 3}'
```
