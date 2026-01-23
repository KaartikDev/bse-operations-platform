import csv
import json
import random
from groq import Groq
from constants import BUCKETS, model
from dotenv import load_dotenv

load_dotenv()

schema = {}
for bucket in BUCKETS:
    schema[bucket] = {"type": "number"}

schema["employer"] = {"type": "string"}

client = Groq()

def read_students_csv():
    with open("students.csv") as f:
        reader = csv.reader(f)
        return [row[0] for row in reader]

application_question = """
Why do you want to be apart of the mentorship program and what companies are you interested? (50 words max, bullets encouraged)
Enter N/A if not applicable.

Tip: Focus on specific projects, skills, or interests so we can pair you with a mentor. 
EX: I'm working on a social media web app, advice from a Meta SWE would help me improve XXX.
"""
old_prompt = f"Extract computer science interest information from the following student's answer to the application question: {application_question}. Rate the person's interest in each computer science field from -1 to 1, where -1 is very negative and 1 is very positive. If they do not state any interest in a field, rate it as 0. For the employer field, extract the name(s) of the company(ies) where the student would like to work at or where their ideal mentor works at."
new_prompt = "Extract computer science interest information from the following student's answer, disinterests, and what their ideal mentor would look like. Rate the person's interest in each computer science field from -1 to 1, where -1 is very negative and 1 is very positive. If they do not state any interest in a field, rate it as 0. For the employer field, extract the name(s) of the company(ies) where the student would like to work at or where their ideal mentor works at."

def get_student_rating(student, prompt):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": str(student),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "computer_science_interest",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": schema,
                    "required": BUCKETS,
                    "additionalProperties": False
                }
            }
        },
    )
    
    rating = json.loads(response.choices[0].message.content or "{}")
    result = {bucket: float(value) for bucket, value in rating.items() if bucket != "employer"}
    result["employer"] = str(rating["employer"])
    return result

if __name__ == "__main__":
    N = 5
    students = read_students_csv()
    for student in random.sample(students, N):
        print(f"Rating: {json.dumps(student, indent=4)}")
        print(json.dumps(get_student_rating(student, old_prompt), indent=4))
