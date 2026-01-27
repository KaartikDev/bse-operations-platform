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


def read_alumni_csv():
    alumni = []

    with open("alumni.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            alumni.append(
                {
                    "company": row[0],
                    "role": row[1],
                    "interests": row[2],
                    "avoid_interests": row[3],
                    "bio": row[4],
                }
            )

    return alumni


prompt = f"""
Extract the following alum's computer science interests using their company, role, interests, interest to avoid, and bio.
Rate the alum's interest in each of the following computer science fields: {", ".join(FIELDS[:-1])} from -1 to 1, where -1 is very negative and 1 is very positive.
If they do not state any interest in a field, rate it as 0.
For the companies field, extract the name(s) of the company(ies) where the alum works at.

Return a JSON object with EXACTLY the following fields: {", ".join(FIELDS)}. All fields must be present and have a value.
"""


def get_alum_rating(alum):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": str(alum),
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
