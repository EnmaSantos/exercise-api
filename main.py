from __future__ import annotations

import os
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

from exercise_store import exercise_store


CACHE_CONTROL = "public, max-age=300, stale-while-revalidate=86400"


app = FastAPI(
    title="Exercise API",
    description="API to fetch exercises and calorie burn information",
    version="1.0.0",
    default_response_class=ORJSONResponse,
)

origins = [
    "http://localhost:3000",
    "https://vitality-vista.vercel.app",
]

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_cache_headers(request, call_next):
    response = await call_next(request)
    cacheable_paths = (
        request.method == "GET"
        and (
            request.url.path == "/health"
            or request.url.path == "/exercises"
            or request.url.path.startswith("/exercises/")
            or request.url.path.startswith("/v2/exercises")
        )
    )
    if (
        cacheable_paths
        and 200 <= response.status_code < 400
        and "cache-control" not in response.headers
    ):
        response.headers["Cache-Control"] = CACHE_CONTROL
    return response


class Exercise(BaseModel):
    name: str
    force: str
    level: str
    mechanic: str
    equipment: str
    primaryMuscles: List[str]
    secondaryMuscles: List[str]
    instructions: List[str]
    category: str
    images: List[str]
    id: int
    calories_per_hour: int
    duration_minutes: int
    total_calories: float


class ExerciseSummary(BaseModel):
    name: str
    force: str
    level: str
    mechanic: str
    equipment: str
    primaryMuscles: List[str]
    secondaryMuscles: List[str]
    category: str
    images: List[str]
    id: int
    calories_per_hour: int
    duration_minutes: int
    total_calories: float


class PaginatedExerciseResponse(BaseModel):
    exercises: List[Exercise]
    currentPage: int
    totalPages: int
    totalCount: int
    limit: int


class V2PaginatedExerciseResponse(BaseModel):
    items: List[ExerciseSummary]
    page: int
    limit: int
    total: int
    totalPages: int


class ExerciseMetaResponse(BaseModel):
    categories: List[str]
    levels: List[str]
    equipment: List[str]
    muscles: List[str]
    totalCount: int


class HealthResponse(BaseModel):
    status: str
    exerciseCount: int
    dataHash: str


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Exercise API!"}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "exerciseCount": exercise_store.total_count,
        "dataHash": exercise_store.data_hash,
    }


@app.get("/exercises", response_model=List[Exercise], tags=["Exercises"])
def get_exercises():
    """Fetch all exercises."""
    return exercise_store.all()


@app.get("/exercises/{exercise_id}", response_model=Exercise, tags=["Exercises"])
def get_exercise_by_id(exercise_id: int):
    """Fetch a single exercise by ID."""
    exercise = exercise_store.get(exercise_id)
    if exercise:
        return exercise
    raise HTTPException(status_code=404, detail="Exercise not found")


@app.get(
    "/exercises/search/{name}",
    response_model=PaginatedExerciseResponse,
    tags=["Exercises"],
)
def search_exercises_by_name(name: str, page: int = 1, limit: int = 20):
    """
    Search exercises by name with pagination.
    - **name**: Search term to look for in exercise names.
    - **page**: Page number (1-based).
    - **limit**: Maximum number of exercises to return per page.
    """
    result = exercise_store.query(
        q=name,
        page=page,
        limit=limit,
        include_full=True,
    )
    return PaginatedExerciseResponse(
        exercises=result["items"],
        currentPage=result["page"],
        totalPages=result["totalPages"],
        totalCount=result["total"],
        limit=result["limit"],
    )


@app.get(
    "/v2/exercises",
    response_model=V2PaginatedExerciseResponse,
    tags=["Exercises v2"],
)
def get_v2_exercises(
    page: int = 1,
    limit: int = 20,
    q: Optional[str] = None,
    category: Optional[str] = None,
    level: Optional[str] = None,
    equipment: Optional[str] = None,
    muscle: Optional[str] = None,
):
    return exercise_store.query(
        q=q,
        page=page,
        limit=limit,
        category=category,
        level=level,
        equipment=equipment,
        muscle=muscle,
    )


@app.get(
    "/v2/exercises/meta",
    response_model=ExerciseMetaResponse,
    tags=["Exercises v2"],
)
def get_v2_exercise_meta():
    return exercise_store.meta()


@app.get(
    "/v2/exercises/{exercise_id}",
    response_model=Exercise,
    tags=["Exercises v2"],
)
def get_v2_exercise_by_id(exercise_id: int):
    exercise = exercise_store.get(exercise_id)
    if exercise:
        return exercise
    raise HTTPException(status_code=404, detail="Exercise not found")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
