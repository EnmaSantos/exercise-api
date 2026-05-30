# Exercise API

FastAPI exercise-data API that fetches, normalizes, and serves exercise metadata through REST endpoints. Built with Python for backend data processing, JSON parsing, data normalization, and API integration.

## Overview

This API builds upon the excellent "Free Exercise DB" dataset, enhancing it with additional functionality and calorie-burning information. The service makes it easy to integrate exercise data into fitness applications, workout planners, or health tracking systems.

## What This Demonstrates

This project demonstrates Python API development, JSON parsing, data normalization, and backend deployment for a fitness-data use case.

## Features

- Access to 800+ exercises with detailed information
- Exercise data includes muscle groups, difficulty levels, equipment requirements, and instructions
- Enhanced with calorie-burning metrics (calories per hour, duration, total calories)
- Easy-to-use RESTful API endpoints
- Fast performance with FastAPI framework
- Automatic API documentation with Swagger UI

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/exercises` | GET | Retrieve all exercises |
| `/exercises/{exercise_id}` | GET | Get a specific exercise by ID |
| `/exercises/search/{name}` | GET | Search exercises by name |

## Exercise Data Structure

Each exercise includes the following information:

```json
{
  "name": "Exercise Name",
  "force": "pull/push",
  "level": "beginner/intermediate/advanced",
  "mechanic": "compound/isolation",
  "equipment": "required equipment",
  "primaryMuscles": ["main muscles targeted"],
  "secondaryMuscles": ["supporting muscles"],
  "instructions": ["step-by-step instructions"],
  "category": "exercise category",
  "images": ["URLs to demonstration images"],
  "id": "unique identifier",
  "calories_per_hour": 354,
  "duration_minutes": 30,
  "total_calories": 177.0
}
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/EnmaSantos/exercise-api.git
   cd exercise-api
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

4. Ensure you have the `fixed_exercises.json` file in your project directory.

5. Run the application:
   ```bash
   python main.py
   ```

   Alternatively, you can use uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`. Interactive API documentation can be accessed at `http://localhost:8000/docs`.

## Usage Examples

### Fetch all exercises

```python
import requests

response = requests.get("http://localhost:8000/exercises")
exercises = response.json()
print(f"Total exercises: {len(exercises)}")
```

### Get an exercise by ID

```python
import requests

exercise_id = 1
response = requests.get(f"http://localhost:8000/exercises/{exercise_id}")
exercise = response.json()
print(f"Exercise name: {exercise['name']}")
print(f"Primary muscles: {', '.join(exercise['primaryMuscles'])}")
```

### Search exercises by name

```python
import requests

search_term = "curl"
response = requests.get(f"http://localhost:8000/exercises/search/{search_term}")
matching_exercises = response.json()
print(f"Found {len(matching_exercises)} exercises with '{search_term}' in the name:")
for exercise in matching_exercises:
    print(f"- {exercise['name']}")
```

## Credits

This project builds upon the "Free Exercise DB" created by Ollie Jennings and maintained by Yuhonas. The original database provides a comprehensive collection of exercises in JSON format with associated images.

- Original project: [Free Exercise DB](https://github.com/yuhonas/free-exercise-db)
- Maintained by: [Yuhonas](https://github.com/yuhonas)

## License

This project follows the same license as the original Free Exercise DB (Unlicense), placing it in the public domain.

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request or open an issue if you find any bugs or have suggestions for improvements.
