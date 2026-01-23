import csv
import json
import random
from groq import Groq
from buckets import BUCKETS
from dotenv import load_dotenv

load_dotenv()

schema = {}
for bucket in BUCKETS:
    schema[bucket] = {"type": "number"}

client = Groq()

def read_alumni_csv():
    people = []

    with open("alumni.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            people.append({
                "company": row[0],
                "role": row[1],
                "interests": row[2],
                "avoid_interests": row[3],
                "bio": row[4],
            })

    return people

def get_alumnus_rating(alumnus):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "Extract computer science interest information from the following alumnus's company, role, interests, interest to avoid, and bio. Rate the person's interest in each computer science field from -1 to 1, where -1 is very negative and 1 is very positive. If they do not state any interest in a field, rate it as 0."
            },
            {
                "role": "user",
                "content": str(alumnus),
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

    return json.loads(response.choices[0].message.content or "{}")

if __name__ == "__main__":
    N = 5
    alumni = read_alumni_csv()
    for alumnus in random.sample(alumni, N):
        print(f"Rating: {json.dumps(alumnus, indent=4)}")
        print(json.dumps(get_alumnus_rating(alumnus), indent=4))
