import pandas as pd
from google import genai
from google.genai import types
import json
import os
import time

GEMINI_API_KEY = "AIzaSyCmZPmrC1U-2DxFO_YgZ2iNZFUugs3iEDU"
client = genai.Client(api_key=GEMINI_API_KEY)

def get_system_instruction():
    return """
You are an expert application reviewer. You are processing a BATCH of student applications.

### SCORING PHILOSOPHY: THE "BELL CURVE"
Evaluate these candidates relative to the criteria. **Bias heavily towards YELLOW.**
- **RED:** Bottom ~10-15% (Lazy, Unserious, "N/A" spam).
- **GREEN:** Top ~10-15% (Specific niche interest, active complex project).
- **YELLOW:** The standard ~70% (Enthusiastic but generic goals like "I want to work at Google").

### OUTPUT FORMAT
Return a raw **JSON ARRAY** of objects. Do not wrap in markdown.
[
  {
    "id": "BSE-123",
    "verdict": "YELLOW",
    "reasoning": "Enthusiastic about web dev but lacks a specific project plan."
  },
  ...
]
"""

def prepare_applicant_text(row):
    """Format a single row into a readable text block."""
    interests = row.get('What are your areas of interests in SWE? (<50 words)\n\nPut N/A if you\'re unsure.', 'N/A')
    needs = row.get('What is something you need mentoring on?  (<100 words) \n\nPut N/A if you\'re unsure.', 'N/A')
    mentor = row.get('What would your ideal mentor look like? Which company would they work at? What are they an expert in? What is their background.  (<100 words)\n\n\nPut N/A if you\'re unsure.', 'N/A')
    plans = row.get('Accepted members of the program will be matched 1:1 with an engineer for at least four 30 min meetings.\n\nWhat would be your plan for each meeting? (<150 words)\n\nPut N/A if you\'re unsure.', 'N/A')
    
    return f"""
    -- Applicant {row.get('BSE ID Number', 'Unknown')} --
    Interests: {interests}
    Needs: {needs}
    Ideal Mentor: {mentor}
    Meeting Plan: {plans}
    """

def process_batch(df_chunk):
    applicants_text = ""
    ids_in_batch = []
    
    for _, row in df_chunk.iterrows():
        uid = str(row.get('BSE ID Number', 'Unknown'))
        ids_in_batch.append(uid)
        applicants_text += prepare_applicant_text(row) + "\n\n"

    prompt = f"{get_system_instruction()}\n\n### BATCH DATA:\n{applicants_text}"

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    max_output_tokens=8192
                )
            )
            return json.loads(response.text)
            
        except Exception as e:
            if "429" in str(e):
                print(f"  Rate limit hit. Waiting 30s...")
                time.sleep(30)
            else:
                print(f"  Batch Error: {e}")
                return [{"id": uid, "verdict": "ERROR", "reasoning": str(e)} for uid in ids_in_batch]
    
    return [{"id": uid, "verdict": "ERROR", "reasoning": "Timeout"} for uid in ids_in_batch]

def main():
    file_path = '/Users/ashwinjoshi/Projects/bse-operations-platform/application-reviewer/Mentee Application Winter 2026 (testing) (Responses) - Form Responses 1.csv'
    
    if not os.path.exists(file_path):
        file_path = 'Mentee Application Winter 2026 (testing) (Responses) - Form Responses 1.csv'
        if not os.path.exists(file_path):
            print("CSV file not found.")
            return

    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} applicants.")

    BATCH_SIZE = 50  # Safe limit for Gemini output tokens
    all_results = []

    for i in range(0, len(df), BATCH_SIZE):
        chunk = df.iloc[i:i + BATCH_SIZE]
        print(f"Processing batch {i} to {i + len(chunk)}...")
        
        batch_results = process_batch(chunk)
        
        if isinstance(batch_results, list):
            all_results.extend(batch_results)
        else:
            print("  Warning: API did not return a list. Skipping batch.")

        time.sleep(20)  # To avoid rate limits

    results_df = pd.DataFrame(all_results)
    
    sort_map = {"GREEN": 0, "YELLOW": 1, "RED": 2, "ERROR": 3}
    if 'verdict' in results_df.columns:
        results_df['sort'] = results_df['verdict'].map(sort_map)
        results_df = results_df.sort_values('sort').drop('sort', axis=1)

    results_df.to_csv('batch_verdicts.csv', index=False)
    print("\nDone! Saved to 'batch_verdicts.csv'")
    print(results_df.head().to_string(index=False))

if __name__ == "__main__":
    main()