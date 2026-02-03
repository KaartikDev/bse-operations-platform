import pandas as pd
from google import genai
from google.genai import types
import json
import os
import time



# 1. API KEY
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# 2. FILE SETTINGS
INPUT_CSV_PATH = '/Users/ashwinjoshi/Projects/bse-operations-platform/application-reviewer/Mentee Application Winter 2026 (testing) (Responses) - Form Responses 1.csv'
OUTPUT_CSV_PATH = 'batch_verdicts.csv'
BATCH_SIZE = 50       # Number of applicants per API call (Max ~50-80 for safety)
RATE_LIMIT_SLEEP = 20 # Seconds to wait between batches

# 3. REVIEWER LOGIC (The "Brain")
# Change this string to alter how the AI judges applicants.
REVIEW_CRITERIA = """
### SCORING PHILOSOPHY
Evaluate these candidates relative to the criteria. **Bias heavily towards YELLOW.**
- **RED:** Bottom ~10-15% (Lazy, Unserious, "N/A" spam, or actively hostile).
- **GREEN:** Top ~10-15% (Exceptional specificity, active/complex niche projects, or clear "Builder" mentality).
- **YELLOW:** The standard ~70% (Enthusiastic but generic goals like "I want to work at Google" or "I want to learn AI").

### JUDGING RULES
- If an applicant writes full sentences and shows genuine interest, they are likely **YELLOW**, not Red.
- **RED** is reserved for one-word answers, gibberish, or zero effort.
- **GREEN** requires evidence of action (e.g., "I am building X using Y stack") or deep niche interest (e.g., "Defense/BioTech").
"""

# 4. CSV COLUMN MAPPING (The "Eyes")
# Map a readable label (Key) to the exact CSV Header (Value).
# If the Google Form questions change, just update the Values here.
CSV_COLUMNS = {
    "Interests": "What are your areas of interests in SWE? (<50 words)\n\nPut N/A if you're unsure.",
    "Mentorship Needs": "What is something you need mentoring on?  (<100 words) \n\nPut N/A if you're unsure.",
    "Ideal Mentor": "What would your ideal mentor look like? Which company would they work at? What are they an expert in? What is their background.  (<100 words)\n\n\nPut N/A if you're unsure.",
    "Meeting Plans": "Accepted members of the program will be matched 1:1 with an engineer for at least four 30 min meetings.\n\nWhat would be your plan for each meeting? (<150 words)\n\nPut N/A if you're unsure."
}

# 5. ID COLUMN NAME
ID_COLUMN = 'BSE ID Number'  # Exact CSV header for unique applicant ID

client = genai.Client(api_key=GEMINI_API_KEY)

def get_system_instruction():
    """Combines user criteria with strict formatting rules."""
    return f"""
You are an expert application reviewer processing a BATCH of student applications.

{REVIEW_CRITERIA}

### OUTPUT FORMAT
Return a raw **JSON ARRAY** of objects. Do not wrap in markdown.
[
  {{
    "id": "BSE-123",
    "verdict": "YELLOW",
    "reasoning": "Enthusiastic about web dev but lacks a specific project plan."
  }},
  ...
]
"""

def prepare_applicant_text(row):
    """Dynamically formats a single row based on CSV_COLUMNS constant."""
    uid_col = ID_COLUMN
    uid = row.get(uid_col, 'Unknown')
    
    text_block = f"-- Applicant {uid} --\n"
    
    for label, csv_header in CSV_COLUMNS.items():
        answer = row.get(csv_header, 'N/A')
        clean_answer = str(answer).replace('\n', ' ').strip()
        text_block += f"{label}: {clean_answer}\n"
        
    return text_block

def process_batch(df_chunk):
    """Sends a batch of applicants to Gemini."""
    applicants_text = ""
    ids_in_batch = []
    
    # 1. Build the text prompt
    for _, row in df_chunk.iterrows():
        uid = str(row.get(ID_COLUMN, 'Unknown'))
        ids_in_batch.append(uid)
        applicants_text += prepare_applicant_text(row) + "\n\n"

    prompt = f"{get_system_instruction()}\n\n### BATCH DATA:\n{applicants_text}"

    # 2. Call API with Retry Logic
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
    # 1. Load Data
    if not os.path.exists(INPUT_CSV_PATH):
        local_path = os.path.basename(INPUT_CSV_PATH)
        if os.path.exists(local_path):
            df = pd.read_csv(local_path)
        else:
            print(f"Error: CSV file not found at {INPUT_CSV_PATH}")
            return
    else:
        df = pd.read_csv(INPUT_CSV_PATH)
        
    print(f"Loaded {len(df)} applicants.")
    print(f"Configuration: Batch Size={BATCH_SIZE}, Bias towards YELLOW.")

    # 2. Process
    all_results = []

    for i in range(0, len(df), BATCH_SIZE):
        chunk = df.iloc[i:i + BATCH_SIZE]
        print(f"Processing batch {i} to {i + len(chunk)}...")
        
        batch_results = process_batch(chunk)
        
        if isinstance(batch_results, list):
            all_results.extend(batch_results)
        else:
            print("  Warning: API did not return a list. Skipping batch.")

        time.sleep(RATE_LIMIT_SLEEP)

    # 3. Sort and Save
    results_df = pd.DataFrame(all_results)
    
    sort_map = {"GREEN": 0, "YELLOW": 1, "RED": 2, "ERROR": 3}
    
    if 'verdict' in results_df.columns:
        results_df['sort'] = results_df['verdict'].map(sort_map)
        results_df = results_df.sort_values('sort').drop('sort', axis=1)

    results_df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"\nDone! Saved to '{OUTPUT_CSV_PATH}'")
    print(results_df.head().to_string(index=False))

if __name__ == "__main__":
    main()