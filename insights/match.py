from alumni import get_alumnus_rating, read_alumni_csv
from evaluate import compute_similarity
from student import get_student_rating, read_students_csv, old_prompt
import random
import json

if __name__ == "__main__":
    N = 10

    print(f"\n=== RATING {N} ALUMNI ===\n")

    alumni_ratings = []
    alumni_info = []
    alumni = read_alumni_csv()
    for alumnus in random.sample(alumni, N):
        print(f"Rating: {json.dumps(alumnus, indent=4)}")
        rating = get_alumnus_rating(alumnus)
        print(json.dumps(rating, indent=4))
        alumni_ratings.append(list(rating.values()))
        alumni_info.append(alumnus)

    print(f"\n=== RATING {N} STUDENTS ===\n")

    student_ratings = []
    student_info = []
    students = read_students_csv()
    for student in random.sample(students, N):
        print(f"Rating: {json.dumps(student, indent=4)}")
        rating = get_student_rating(student, old_prompt)
        print(json.dumps(rating, indent=4))
        student_ratings.append(list(rating.values()))
        student_info.append(student)

    print(f"\n=== COMPUTING BEST MATCHES ===\n")
    for student_rating, student_info in zip(student_ratings, student_info):
        best_match = max(alumni_ratings, key=lambda x: compute_similarity(student_rating, x))
        print(f"Best match for student:\n{json.dumps(student_info, indent=4)}\nis:\n{json.dumps(alumni_info[alumni_ratings.index(best_match)], indent=4)}")
        del alumni_info[alumni_ratings.index(best_match)]
        del alumni_ratings[alumni_ratings.index(best_match)]
