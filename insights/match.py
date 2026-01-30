from typing import Union
from alumni import get_alum_rating, read_alumni_csv
from student import (
    get_student_rating,
    new_prompt,
    old_prompt,
    read_students_csv,
)
from constants import (
    STUDENT_TEST_CASES,
    FIELD_WEIGHT,
    COMPANY_WEIGHT,
    CLASH_PENALTY,
    FIELDS,
    STRONG_MATCH_THRESHOLD,
    WEAK_MATCH_THRESHOLD,
    USE_CSV_STUDENTS,
    N,
)
import random
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.optimize import linear_sum_assignment


def optimal_assignment(
    student_ratings: list[list[Union[float, list[str]]]],
    alum_ratings: list[list[Union[float, list[str]]]],
) -> list[tuple[int, int]]:
    n = len(student_ratings)
    cost = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            cost[i, j] = -compute_similarity(student_ratings[i], alum_ratings[j])

    row_i, col_i = linear_sum_assignment(cost)
    return list(zip(row_i.tolist(), col_i.tolist()))


def compute_similarity(
    student_vals: list[Union[float, list[str]]],
    alum_vals: list[Union[float, list[str]]],
) -> float:
    vec1 = np.array(student_vals[:-1])
    vec2 = np.array(alum_vals[:-1])
    field_similarity = cosine_similarity(vec1.reshape(1, -1), vec2.reshape(1, -1))[0][0]

    companies1 = normalize_companies(student_vals[-1])
    companies2 = normalize_companies(alum_vals[-1])
    common_companies = len(companies1 & companies2)

    penalty = 0
    for i in range(len(vec1)):
        if vec1[i] * vec2[i] < 0:
            penalty += CLASH_PENALTY

    return FIELD_WEIGHT * field_similarity + COMPANY_WEIGHT * common_companies - penalty


# TODO
def normalize_companies(companies: list[str]) -> set[str]:
    return {c.strip().lower() for c in companies}


def get_match_tier(similarity: float) -> str:
    if similarity >= STRONG_MATCH_THRESHOLD:
        return "strong"
    if similarity <= WEAK_MATCH_THRESHOLD:
        return "weak"
    return "ok"


def compute_match_explanation(
    student_vals: list[Union[float, list[str]]],
    alum_vals: list[Union[float, list[str]]],
) -> dict:
    vec1 = student_vals[:-1]
    vec2 = alum_vals[:-1]

    aligned_fields = [
        (FIELDS[i], vec1[i], vec2[i]) for i in range(len(vec1)) if vec1[i] * vec2[i] > 0
    ]

    clash_fields = [
        (FIELDS[i], vec1[i], vec2[i]) for i in range(len(vec1)) if vec1[i] * vec2[i] < 0
    ]

    companies1 = normalize_companies(student_vals[-1])
    companies2 = normalize_companies(alum_vals[-1])
    common_companies = list(companies1 & companies2)

    return {
        "aligned_fields": aligned_fields,
        "clash_fields": clash_fields,
        "common_companies": common_companies,
    }


if __name__ == "__main__":
    if USE_CSV_STUDENTS:
        students = random.sample(read_students_csv(), N)
        student_prompt = old_prompt
        print(f"\n=== RATING {len(students)} STUDENTS (from CSV) ===\n")
    else:
        students = random.sample(STUDENT_TEST_CASES, N)
        student_prompt = new_prompt
        print(f"\n=== RATING {len(students)} STUDENTS (from test cases) ===\n")

    student_ratings: list[list[Union[float, list[str]]]] = []
    for student in students:
        rating = get_student_rating(student, student_prompt)
        student_ratings.append(list(rating.values()))

    alumni = random.sample(read_alumni_csv(), N)
    print(f"\n=== RATING {len(alumni)} ALUMNI (from CSV) ===\n")

    alum_ratings: list[list[Union[float, list[str]]]] = []
    for alum in alumni:
        rating = get_alum_rating(alum)
        alum_ratings.append(list(rating.values()))

    print("\n=== OPTIMAL ASSIGNMENT (Hungarian) ===\n")
    pairs = optimal_assignment(student_ratings, alum_ratings)

    tier_counts = {"strong": 0, "ok": 0, "weak": 0}

    for student_i, alum_i in pairs:
        student_info = students[student_i]
        alum_info = alumni[alum_i]
        student_vals = student_ratings[student_i]
        alum_vals = alum_ratings[alum_i]

        similarity = compute_similarity(student_vals, alum_vals)
        tier = get_match_tier(similarity)
        tier_counts[tier] += 1

        explanation = compute_match_explanation(student_vals, alum_vals)

        print(
            f"[{tier.upper()}] Student #{student_i} <-> Alum #{alum_i} (similarity={similarity})"
        )
        print(
            f"  Student: {json.dumps(student_info, indent=4) if isinstance(student_info, dict) else student_info!r}"
        )
        print(f"  Student values: {json.dumps(student_vals, indent=4)}")
        print(f"  Alum: {json.dumps(alum_info, indent=4)}")
        print(f"  Alum values: {json.dumps(alum_vals, indent=4)}")
        print(
            f"  Why: aligned_fields={explanation['aligned_fields']}, clash_fields={explanation['clash_fields']}, common_companies={explanation['common_companies']}"
        )
        print()

    print("\n=== SUMMARY ===")
    print(f"  Tier counts: {tier_counts}")
