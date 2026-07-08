from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_LIMIT = 20
MAX_LIMIT = 100
DATA_PATH = Path(__file__).with_name("fixed_exercises.json")
SUMMARY_EXCLUDED_FIELDS = {"instructions"}


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def _sorted_values(values: Iterable[str]) -> list[str]:
    return sorted(value for value in values if value)


def _clamp_page(page: int) -> int:
    return page if page >= 1 else 1


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return DEFAULT_LIMIT
    return min(limit, MAX_LIMIT)


@dataclass(frozen=True)
class IndexedExercise:
    exercise: dict[str, Any]
    summary: dict[str, Any]
    exercise_id: int
    name: str
    category: str
    level: str
    equipment: str
    muscles: frozenset[str]


class ExerciseStore:
    def __init__(self, data_path: Path = DATA_PATH) -> None:
        self.data_path = data_path
        self.data_hash = self._hash_file(data_path)
        self._exercises = self._load_exercises(data_path)
        self._indexed = self._build_index(self._exercises)
        self._by_id = {item.exercise_id: item.exercise for item in self._indexed}
        self._meta = self._build_meta(self._indexed)

    @staticmethod
    def _hash_file(data_path: Path) -> str:
        return hashlib.sha256(data_path.read_bytes()).hexdigest()

    @staticmethod
    def _load_exercises(data_path: Path) -> list[dict[str, Any]]:
        with data_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _build_index(exercises: list[dict[str, Any]]) -> list[IndexedExercise]:
        indexed: list[IndexedExercise] = []
        for exercise in exercises:
            exercise_id = int(exercise["id"])
            primary_muscles = exercise.get("primaryMuscles", [])
            secondary_muscles = exercise.get("secondaryMuscles", [])
            muscles = frozenset(
                _normalize(muscle) for muscle in [*primary_muscles, *secondary_muscles]
            )
            summary = {
                key: value
                for key, value in exercise.items()
                if key not in SUMMARY_EXCLUDED_FIELDS
            }
            indexed.append(
                IndexedExercise(
                    exercise=exercise,
                    summary=summary,
                    exercise_id=exercise_id,
                    name=_normalize(exercise.get("name")),
                    category=_normalize(exercise.get("category")),
                    level=_normalize(exercise.get("level")),
                    equipment=_normalize(exercise.get("equipment")),
                    muscles=muscles,
                )
            )
        return indexed

    @staticmethod
    def _build_meta(indexed: list[IndexedExercise]) -> dict[str, Any]:
        categories = {item.category for item in indexed}
        levels = {item.level for item in indexed}
        equipment = {item.equipment for item in indexed}
        muscles = set[str]()
        for item in indexed:
            muscles.update(item.muscles)

        return {
            "categories": _sorted_values(categories),
            "levels": _sorted_values(levels),
            "equipment": _sorted_values(equipment),
            "muscles": _sorted_values(muscles),
            "totalCount": len(indexed),
        }

    @property
    def total_count(self) -> int:
        return len(self._exercises)

    def all(self) -> list[dict[str, Any]]:
        return self._exercises

    def get(self, exercise_id: int) -> dict[str, Any] | None:
        return self._by_id.get(exercise_id)

    def meta(self) -> dict[str, Any]:
        return self._meta

    def query(
        self,
        *,
        page: int = 1,
        limit: int = DEFAULT_LIMIT,
        q: str | None = None,
        category: str | None = None,
        level: str | None = None,
        equipment: str | None = None,
        muscle: str | None = None,
        include_full: bool = False,
    ) -> dict[str, Any]:
        page = _clamp_page(page)
        limit = _clamp_limit(limit)

        search = _normalize(q)
        category_filter = _normalize(category)
        level_filter = _normalize(level)
        equipment_filter = _normalize(equipment)
        muscle_filter = _normalize(muscle)

        matches = [
            item.exercise if include_full else item.summary
            for item in self._indexed
            if self._matches(
                item,
                search=search,
                category=category_filter,
                level=level_filter,
                equipment=equipment_filter,
                muscle=muscle_filter,
            )
        ]

        total = len(matches)
        total_pages = math.ceil(total / limit) if total else 1
        start = (page - 1) * limit
        end = start + limit

        return {
            "items": matches[start:end],
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages,
        }

    @staticmethod
    def _matches(
        item: IndexedExercise,
        *,
        search: str,
        category: str,
        level: str,
        equipment: str,
        muscle: str,
    ) -> bool:
        if search and search not in item.name:
            return False
        if category and category != item.category:
            return False
        if level and level != item.level:
            return False
        if equipment and equipment != item.equipment:
            return False
        if muscle and muscle not in item.muscles:
            return False
        return True


exercise_store = ExerciseStore()
