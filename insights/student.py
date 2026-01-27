import csv
import json
from groq import Groq
from constants import FIELDS, model
from dotenv import load_dotenv

load_dotenv()
client = Groq()

schema = {}
for field in FIELDS:
    schema[field] = {"type": "number"}

schema["companies"] = {"type": "array"}


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

old_prompt = f"""
Extract the following student's computer science interests using their answer to the following application question: {application_question}.
Rate the student's interest in each of the following computer science fields: {", ".join(FIELDS[:-1])} from -1 to 1, where -1 is very negative and 1 is very positive.
If they do not state any interest in a field, rate it as 0.
For the companies field, extract the name(s) of the company(ies) where the student would like to work at or where their ideal mentor works at.

Return a JSON object with EXACTLY the following fields: {", ".join(FIELDS)}. All fields must be present and have a value.
"""

new_prompt = f"""
Extract the following student's computer science interests using their interests, disinterests, and what their ideal mentor would look like.
Rate the student's interest in each of the following computer science fields: {", ".join(FIELDS[:-1])} from -1 to 1, where -1 is very negative and 1 is very positive.
If they do not state any interest in a field, rate it as 0.
For the companies field, extract the name(s) of the company(ies) where the student would like to work at or where their ideal mentor works at.

Return a JSON object with EXACTLY the following fields: {", ".join(FIELDS)}. All fields must be present and have a value.
"""


def get_student_rating(student, prompt):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
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
                    "required": FIELDS,
                    "additionalProperties": False,
                },
            },
        },
    )

    result = json.loads(response.choices[0].message.content)
    rating = {
        field: float(value) for field, value in result.items() if field != "companies"
    }
    rating["companies"] = list(result["companies"])
    return rating
