# Mergington High School Activities API

A FastAPI application for viewing extracurricular activities and managing student registrations through teacher accounts.

## Features

- View all available extracurricular activities
- Filter activities by day and start/end time
- Sign students up for activities and unregister them through teacher accounts

## Getting Started

Run these commands from the repository root, not from `src/`.

1. Install the dependencies:

   ```
   python -m pip install -r requirements.txt
   ```

2. Ensure MongoDB is running at `mongodb://localhost:27017/`. The repository's
   development container installs and starts MongoDB automatically. For local
   development outside the container, install and start MongoDB separately.

3. Run the application:

   ```
   python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 8000
   ```

4. Open your browser and go to:
   - Activities website: http://localhost:8000/
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/activities` | Get activity details and participant lists; optionally filter with `day`, `start_time`, and `end_time` |
| GET | `/activities/days` | Get the available activity days |
| POST | `/activities/{activity_name}/signup` | Sign up a student; requires `email` and a valid `teacher_username` query parameter |
| POST | `/activities/{activity_name}/unregister` | Unregister a student; requires `email` and a valid `teacher_username` query parameter |
| POST | `/auth/login` | Check a teacher's credentials using `username` and `password` query parameters |
| GET | `/auth/check-session` | Check whether the teacher supplied by the `username` query parameter exists |

Use the interactive API documentation to supply query parameters and URL-encode
activity names containing spaces.

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Teachers** - Uses username as identifier:
   - Display name
   - Hashed password
   - Role

Student email addresses are stored in each activity's participant list; there is
no separate student collection.

Data is stored in the `activities` and `teachers` collections of the
`mergington_high` MongoDB database. Restarting the API does not reset this data.
On startup, sample activities and teacher accounts are inserted only when their
respective collection is empty.
