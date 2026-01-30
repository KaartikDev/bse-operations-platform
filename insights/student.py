import csv
import json
from typing import Union
from groq import Groq
from constants import FIELDS, MODEL
from dotenv import load_dotenv
from alumni import result_to_rating, extract_json_from_text

load_dotenv()
client = Groq()

schema = {}
for field in FIELDS:
    schema[field] = {"type": "number"}

schema["companies"] = {"type": "array", "items": {"type": "string"}}


def read_students_csv() -> list[str]:
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
Output ONLY a JSON object. No reasoning or other text.

Extract the student's computer science interests from their answer to the application question: {application_question}.

Important:
- Rate each field using scores of -1, -0.5, 0, 0.5, and 1 in order to represent very negative, negative, neutral, positive, and very positive interest respectively.
- If they explicitly say they want to avoid or are not interested in a field, assign a negative score (-0.5 or -1). Do not rate the field as 0.
- If they do not mention a field, rate the field as 0.
- If they express any interest in a field, assign a positive score (0.5 or 1). Do not rate the field as 0.
- For companies: extract every company (or type of company like FAANG) they say they are interested in or where they want their mentor to work at. Use the commonly used name of the company(ies). For example, "Meta" should be "Facebook" and "ex Microsoft" should be "Microsoft".

Return a JSON object with EXACTLY the following fields: {", ".join(FIELDS)}. All fields must be present and have a value.
Use decimal numbers for every numeric field (e.g. -1.0, -0.5, 0.0, 0.5, 1.0), not integers. The "companies" field must be an array of strings (company names). Reply with ONLY the JSON object, nothing else.
"""

new_prompt = f"""
Output ONLY a JSON object. No reasoning or other text.

Extract the student's computer science interests from their stated interests, disinterests, and ideal mentor description.

Important:
- Rate each field using scores of -1, -0.5, 0, 0.5, and 1 in order to represent very negative, negative, neutral, positive, and very positive interest respectively.
- Disinterests must produce negative scores (-0.5 or -1) for those fields. Do not rate the field as 0.
- If they do not mention a field, rate the field as 0.
- Interests must produce positive scores (0.5 or 1) for those fields. Do not rate the field as 0.
- Any interests and disinterests can be extracted from the student's ideal mentor description as well.
- For companies: extract every company (or type of company like FAANG) they say they are interested in or where they want their mentor to work at. Use the commonly used name of the company(ies). For example, "Meta" should be "Facebook" and "ex Microsoft" should be "Microsoft".

Return a JSON object with EXACTLY the following fields: {", ".join(FIELDS)}. All fields must be present and have a value.
Use decimal numbers for every numeric field (e.g. -1.0, -0.5, 0.0, 0.5, 1.0), not integers. The "companies" field must be an array of strings (company names). Reply with ONLY the JSON object, nothing else.
"""


def get_student_rating(
    student: Union[str, dict], prompt: str, retries: int = 3
) -> dict:
    from groq import BadRequestError

    content = str(student)
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "computer_science_interests_rating",
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
            return result_to_rating(result)
        except BadRequestError as e:
            err_body = e.body if isinstance(getattr(e, "body", None), dict) else {}
            code = err_body.get("error", {}).get("code")
            failed = err_body.get("error", {}).get("failed_generation", "")
            if code == "output_parse_failed" and failed:
                extracted = extract_json_from_text(failed)
                if extracted and all(k in extracted for k in FIELDS):
                    return result_to_rating(extracted)
            if code == "json_validate_failed" and attempt < retries - 1:
                content += "\n\n[Reminder: respond with decimal numbers only for numeric fields, e.g. 0.0 not 0. Companies must be an array of strings.]"
                continue
            if code == "output_parse_failed" and attempt < retries - 1:
                content += "\n\n[Output ONLY the JSON object. No other text.]"
                continue
            raise
    raise RuntimeError("get_student_rating failed after retries")
