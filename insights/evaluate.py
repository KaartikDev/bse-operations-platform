import json
from random import random
from alumni import get_alum_rating, read_alumni_csv
from student import get_student_rating, new_prompt
from constants import (
    FIELDS,
    STUDENT_TEST_CASES,
    EXPECTED_POS_THRESHOLD,
    EXPECTED_NEG_THRESHOLD,
    CONSISTENCY_RUNS,
    CONSISTENCY_THRESHOLD,
)
from match import compute_similarity


def validate_rating(rating):
    errors = []

    for field in FIELDS:
        if field not in rating:
            errors.append(f"Missing field: {field}")
        elif field == "companies":
            if not isinstance(rating[field], list):
                errors.append(
                    f"Invalid type for companies: expected list, got {type(rating[field])}"
                )
        elif not isinstance(rating[field], float):
            errors.append(
                f"Invalid type for {field}: expected float, got {type(rating[field])}"
            )
        elif rating[field] < -1 or rating[field] > 1:
            errors.append(
                f"Value out of range for {field}: {rating[field]} (expected -1 to 1)"
            )

    extra_keys = [key for key in rating.keys() if key not in FIELDS]
    if extra_keys:
        errors.append(f"Extra properties found: {', '.join(extra_keys)}")

    return errors


def check_reasonableness(rating, expected_pos, expected_neg, expected_companies):
    issues = []

    for field in expected_pos:
        if rating[field] < EXPECTED_POS_THRESHOLD:
            issues.append(f"Expected high rating for {field}, got {rating[field]}")

    for field in expected_neg:
        if rating[field] > EXPECTED_NEG_THRESHOLD:
            issues.append(f"Expected low rating for {field}, got {rating[field]}")

    for company in expected_companies:
        if company.lower().strip() not in [
            c.lower().strip() for c in rating["companies"]
        ]:
            issues.append(
                f"Expected company {company} not found in {rating['companies']}"
            )

    return issues


def test_consistency(rating_fn, input, prompt=None):
    results = []

    for i in range(CONSISTENCY_RUNS):
        if prompt is not None:
            rating = rating_fn(input, prompt)
        else:
            rating = rating_fn(input)
        results.append(list(rating.values()))

    similarities = []

    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            similarity = compute_similarity(results[i], results[j])
            similarities.append(similarity)

    return {
        "avg_similarity": sum(similarities) / len(similarities),
        "min_similarity": min(similarities),
    }


def evaluate(rating, person, rating_fn, prompt=None):
    print("  Validating rating...")
    errors = validate_rating(rating)
    if errors:
        print(f"  ❌ Errors: {', '.join(errors)}")
    else:
        print("  ✅ Valid rating")

    print("  Checking reasonableness...")
    issues = check_reasonableness(
        rating,
        person["expected_pos"],
        person["expected_neg"],
        person["expected_employer"],
    )
    if issues:
        print(f"  ❌ Issues: {', '.join(issues)}")
    else:
        print("  ✅ Reasonable rating")

    print(f"  Testing consistency ({CONSISTENCY_RUNS} runs)...")
    consistency = test_consistency(rating_fn, person["input"], prompt)
    print(f"  Average similarity: {consistency['avg_similarity']}")
    print(f"  Min similarity: {consistency['min_similarity']}")
    if consistency["avg_similarity"] > CONSISTENCY_THRESHOLD:
        print("  ✅ Consistent rating")
    else:
        print("  ❌ Low consistency")


if __name__ == "__main__":
    N = 10

    print(f"\n=== EVALUATING {N} ALUMNI ===\n")

    alumni = read_alumni_csv()
    for alum in random.sample(alumni, N):
        print(f"Evaluating: {json.dumps(alum, indent=4)}")
        rating = get_alum_rating(alum)
        print(json.dumps(rating, indent=4))
        evaluate(rating, alum, get_alum_rating)

    print(f"\n=== EVALUATING {N} STUDENTS ===\n")

    students = STUDENT_TEST_CASES
    for student in random.sample(students, N):
        print(f"Evaluating: {json.dumps(student, indent=4)}")
        rating = get_student_rating(student, new_prompt)
        print(json.dumps(rating, indent=4))
        evaluate(rating, student, get_student_rating, new_prompt)
