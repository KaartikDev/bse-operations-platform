import csv
import json
from typing import Optional
from groq import Groq
from constants import FIELDS, MODEL
from dotenv import load_dotenv

load_dotenv()
client = Groq()

schema = {}
for field in FIELDS:
    schema[field] = {"type": "number"}
schema["companies"] = {"type": "array", "items": {"type": "string"}}


def read_alumni_csv() -> list[dict]:
    alumni = []

    with open("alumni.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            alumni.append(
                {
                    "company": row[0],
                    "role": row[1],
                    "interests": row[2],
                    "disinterests": row[3],
                    "bio": row[4],
                }
            )

    return alumni


prompt = f"""
Output ONLY a JSON object. No reasoning or other text.

Extract the alum's computer science interests from their company, role, interests, interests to avoid, and bio.

Important:
- Rate each field using scores of -1, -0.5, 0, 0.5, and 1 in order to represent very negative, negative, neutral, positive, and very positive interest respectively.
- If a company specializes in a field, rate the field more positively.
- If the alum has a role that is related to a field, rate the field more positively.
- Interests must produce positive scores (0.5 or 1) for those fields. Do not rate the field as 0.
- If they do not mention a field, rate the field as 0.
- Disinterests must produce negative scores (-0.5 or -1) for those fields. Do not rate the field as 0.
- Any interests and disinterests can be extracted from the alum's bio as well.
- For companies: extract the name(s) of the company(ies) where the alum works at. Use the commonly used name of the company(ies). For example, "Meta" should be "Facebook" and "ex Microsoft" should be "Microsoft".

Return a JSON object with EXACTLY the following fields: {", ".join(FIELDS)}. All fields must be present and have a value.
Use decimal numbers for every numeric field (e.g. -1.0, -0.5, 0.0, 0.5, 1.0), not integers. The "companies" field must be an array of strings (company names). Reply with ONLY the JSON object, nothing else.
"""


def extract_json_from_text(text: str) -> Optional[dict]:
    if not text:
        return None
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def result_to_rating(result: dict) -> dict:
    rating = {
        field: float(value) for field, value in result.items() if field != "companies"
    }
    rating["companies"] = [str(c) for c in result.get("companies", [])]
    return rating


def get_alum_rating(alum: dict, retries: int = 3) -> dict:
    from groq import BadRequestError

    content = str(alum)
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
    raise RuntimeError("get_alum_rating failed after retries")
