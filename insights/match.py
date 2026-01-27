from alumni import get_alum_rating, read_alumni_csv
from student import get_student_rating, new_prompt
from constants import STUDENT_TEST_CASES, FIELD_WEIGHT, COMPANY_WEIGHT
import random
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def compute_similarity(rating1, rating2):
    field_similarity = cosine_similarity(
        np.array(rating1[:-1]).reshape(1, -1), np.array(rating2[:-1]).reshape(1, -1)
    )[0][0]
    common_companies = list(set(rating1[:-1]) & set(rating2[:-1]))

    return FIELD_WEIGHT * field_similarity + COMPANY_WEIGHT * len(common_companies)


def freeze(obj):
    if isinstance(obj, dict):
        return frozenset((k, freeze(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return tuple(freeze(v) for v in obj)
    return obj


def thaw(obj):
    if isinstance(obj, frozenset):
        return {k: thaw(v) for k, v in obj}
    if isinstance(obj, tuple):
        return [thaw(v) for v in obj]
    return obj


if __name__ == "__main__":
    N = 10

    print(f"\n=== RATING {N} ALUMNI ===\n")

    alumni_ratings = {}

    alumni = read_alumni_csv()
    for alum in random.sample(alumni, N):
        print(f"Rating: {json.dumps(alum, indent=4)}")
        rating = get_alum_rating(alum)
        print(json.dumps(rating, indent=4))
        alumni_ratings[freeze(alum)] = list(rating.values())

    print(f"\n=== RATING {N} STUDENTS ===\n")

    student_ratings = {}

    students = STUDENT_TEST_CASES
    for student in random.sample(students, N):
        print(f"Rating: {json.dumps(student, indent=4)}")
        rating = get_student_rating(student, new_prompt)
        print(json.dumps(rating, indent=4))
        student_ratings[freeze(student)] = list(rating.values())

    print("\n=== COMPUTING BEST MATCHES ===\n")

    for student_info, student_values in student_ratings.items():
        best_match = max(
            alumni_ratings.items(),
            key=lambda alum_rating: compute_similarity(student_values, alum_rating[1]),
        )
        print(
            f"Best match for student:\n{json.dumps(thaw(student_info), indent=4)}\nis:\n{json.dumps(thaw(best_match[0]), indent=4)}"
        )
        del alumni_ratings[best_match[0]]
