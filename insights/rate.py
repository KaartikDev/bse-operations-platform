from alumni import get_alumnus_rating, read_alumni_csv
from student import get_student_rating, read_students_csv
import random
import json

if __name__ == "__main__":
    N = 5

    print(f"\n=== RATING {N} ALUMNI ===\n")

    alumni = read_alumni_csv()
    for alumnus in random.sample(alumni, N):
        print(f"Rating: {json.dumps(alumnus, indent=4)}")
        print(json.dumps(get_alumnus_rating(alumnus), indent=4))

    print(f"\n=== RATING {N} STUDENTS ===\n")

    students = read_students_csv()
    for student in random.sample(students, N):
        print(f"Rating: {json.dumps(student, indent=4)}")
        print(json.dumps(get_student_rating(student), indent=4))
