import json
from re import I
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from difflib import SequenceMatcher
from alumni import get_alumnus_rating
from student import get_student_rating, new_prompt
from constants import BUCKETS

ALUMNI_TEST_CASES = [
  {
    "input": {
      "company": "Datadog",
      "role": "Software engineer (distributed systems and query engines)",
      "interests": "No preference",
      "interestToAvoid": "People obsessed with AI",
      "bio": "I am a UCLA alumn working as a Software Engineer at Datadog. I work on distributed query engines and execution. I am excited to help students learn more about the field."
    },
    "expected_pos": ["systems_programming", "databases_and_data_management"],
    "expected_neg": ["artificial_intelligence_and_machine_learning"],
    "expected_employer": ["Datadog"]
  },
  {
    "input": {
      "company": "Pinterest, UC Berkeley",
      "role": "Machine learning engineer (Pinterest Visual Search), lecturer (UC Berkeley, Data Science Undergraduate Studies)",
      "interests": "Preferably someone interested in some of the following: software engineering, machine learning / artificial intelligence, computer vision, recommendation systems, research, grad school, industry vs academia, teaching.",
      "interestToAvoid": "N/A",
      "bio": "Hi! I'm a UCLA alum (Master's in Computer Science, 2016, with focus in AI/ML and computer vision) currently working as a machine learning engineer at Pinterest's Visual Search team. I also teach part-time at UC Berkeley (Data Science Undergraduate Studies program), where I have taught an Intro to Python and an Intro to Deep Learning course. I'm looking forward to help students that are curious about any of the following: AI/ML/computer-vision/recommendation-systems, education, industry vs academia/grad-school, and/or what it's like working in industry! In my free time, I enjoy playing music (piano, bass, guitar, singing), video games, and watching movies (I love Pixar movies, and animation/film in general!)."
    },
    "expected_pos": ["artificial_intelligence_and_machine_learning", "education_and_teaching", "research_and_academia"],
    "expected_neg": [],
    "expected_employer": ["Pinterest", "UC Berkeley"]
  },
  {
    "input": {
      "company": "Self-employed (currently on contract with Varda and Relativity)",
      "role": "Software Consultant",
      "interests": "Prefer students interested in embedded software but this is not a hard requirement.",
      "interestToAvoid": "Would like to avoid students solely interested in AI as that's not where my expertise lies.",
      "bio": "I'm a UCLA alum who previously worked as a Flight Software Engineer at SpaceX and currently works as a consultant at Varda Space Industries, and Relativity; excited to provide guidance on embedded software development, and the Aerospace & Defense industry."
    },
    "expected_pos": ["embedded_systems_and_iot"],
    "expected_neg": ["artificial_intelligence_and_machine_learning"],
    "expected_employer": ["Varda", "Relativity"]
  },
  {
    "input": {
      "company": "Veeva",
      "role": "",
      "interests": "N/A",
      "interestToAvoid": "N/A",
      "bio": "I'm a software engineer at Veeva Systems, happy to talk about getting into industry or anything research!"
    },
    "expected_pos": ["research_and_academia"],
    "expected_neg": [],
    "expected_employer": ["Veeva"]
  },
  {
    "input": {
      "company": "intuit",
      "role": "Sr. Software Engineer",
      "interests": "CS major?",
      "interestToAvoid": "n.a",
      "bio": "I'm a software engineer at intuit, though i've worked at 10+ companies, startups and had higher level roles, have worked web/backend/android mobile and am happy to chat about anything"
    },
    "expected_pos": ["full_stack_web_development", "backend_development", "mobile_development"],
    "expected_neg": [],
    "expected_employer": ["Intuit"]
  },
]

STUDENT_TEST_CASES = [
  {
    "input": {
      "interests": "AI/ML, DevOps, Systems Engineering, Network Engineering, Biotech, Firmware, Hardware",
      "disinterests": "Crypto",
      "ideal_mentor": "They would work at any company, whether Big Tech or a startup. They would be knowledgeable in many fields but hopefully at least full-stack. I don't care much about their background, just whether they are able to assist and connect with me."
    },
    "expected_pos": ["artificial_intelligence_and_machine_learning", "devops_and_cloud_infrastructure", "systems_programming", "computational_biology", "embedded_systems_and_iot", "computer_hardware_and_architecture"],
    "expected_neg": ["cryptocurrency_and_blockchain"],
    "expected_employer": []
  },
  {
    "input": {
      "interests": "Backend and infrastructure engineering, with a focus on scalable systems, APIs, and data pipelines. Interested in developer platforms, reliability, and performance critical services. Enjoy building tools that support large numbers of users and enable other engineers to move faster.",
      "disinterests": "N/A",
      "ideal_mentor": "I’m looking for mentorship on navigating the path to big tech roles, including technical interview preparation and long term career positioning. I’d also value guidance on planning coursework strategically and weighing the tradeoffs between industry experience and pursuing graduate school."
    },
    "expected_pos": ["backend_development", "databases_and_data_management"],
    "expected_neg": [],
    "expected_employer": []
  },
  {
    "input": {
      "interests": "Mobile/iOS development, game development",
      "disinterests": "Operating systems, compilers, anything to do with hardware/memory",
      "ideal_mentor": "Someone from a game development company like Blizzard, etc., expert in developing games and increasing performance"
    },
    "expected_pos": ["mobile_development", "game_development"],
    "expected_neg": ["systems_programming", "computer_hardware_and_architecture"],
    "expected_employer": ["Blizzard"]
  },
]

EXPECTED_POS_THRESHOLD = 0.25  # positive interests should be at least 0.25
EXPECTED_NEG_THRESHOLD = -0.25  # negative interests should be at most -0.25
CONSISTENCY_RUNS = 3  # number of runs to test consistency
CONSISTENCY_THRESHOLD = 0.75  # consistency should be at least 0.75
NUMERIC_WEIGHT = 0.9 # weight of numeric similarity
EMPLOYER_WEIGHT = 0.1 # weight of employer similarity

def validate_rating(rating):
    errors = []
    
    for bucket in BUCKETS:
        if bucket not in rating:
            errors.append(f"Missing bucket: {bucket}")
        elif bucket == "employer":
            if not isinstance(rating[bucket], str):
                errors.append(f"Invalid type for employer: expected string, got {type(rating[bucket])}")
        elif not isinstance(rating[bucket], (int, float)):
            errors.append(f"Invalid type for {bucket}: expected number, got {type(rating[bucket])}")
        elif rating[bucket] < -1 or rating[bucket] > 1:
            errors.append(f"Value out of range for {bucket}: {rating[bucket]} (expected -1 to 1)")
    
    extra_keys = [key for key in rating.keys() if key not in BUCKETS]
    if extra_keys:
        errors.append(f"Extra properties found: {', '.join(extra_keys)}")
    
    return errors

def check_reasonableness(rating, expected_pos, expected_neg, expected_employer):
    issues = []
    
    for bucket in expected_pos:
        if rating[bucket] < EXPECTED_POS_THRESHOLD:
            issues.append(f"Expected high rating for {bucket}, got {rating[bucket]}")
    
    for bucket in expected_neg:
        if rating[bucket] > EXPECTED_NEG_THRESHOLD:
            issues.append(f"Expected low rating for {bucket}, got {rating[bucket]}")

    for employer in expected_employer:
        if employer.lower().strip() not in rating["employer"].lower().strip():
            issues.append(f"Expected employer {employer} not found in {rating['employer']}")
    
    return issues

def compute_similarity(rating1, rating2):
    numeric_similarity = cosine_similarity(np.array(rating1[:-1]).reshape(1, -1), np.array(rating2[:-1]).reshape(1, -1))[0][0]
    emp_similarity = employer_similarity(rating1[-1], rating2[-1])

    return NUMERIC_WEIGHT * numeric_similarity + EMPLOYER_WEIGHT * emp_similarity

def employer_similarity(employer1, employer2):
    if not employer1 or not employer2:
        return 0.0
    
    return SequenceMatcher(None, employer1.lower().strip(), employer2.lower().strip()).ratio()

def test_consistency(rating_fn, input, prompt=None):
    results = []
    
    for i in range(CONSISTENCY_RUNS):
        if prompt is not None:
            rating = rating_fn(input, prompt)
        else:
            rating = rating_fn(input)
        results.append(list(rating.values()))
    
    similarities = []
    
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            similarity = compute_similarity(results[i], results[j])
            similarities.append(similarity)
    
    return {
        "avgSimilarity": sum(similarities) / len(similarities),
        "minSimilarity": min(similarities),
    }

def get_evaluation(rating, person, rating_fn, prompt=None):
    print("  Validating rating...")
    errors = validate_rating(rating)
    if errors:
        print(f"  ❌ Errors: {', '.join(errors)}")
    else:
        print(f"  ✅ Valid")

    print("  Checking reasonableness...")
    issues = check_reasonableness(rating, person["expected_pos"], person["expected_neg"], person["expected_employer"])
    if issues:
        print(f"  ❌ Issues: {', '.join(issues)}")
    else:
        print(f"  ✅ Reasonable")
    
    print(f"  Testing consistency ({CONSISTENCY_RUNS} runs)...")
    consistency = test_consistency(rating_fn, person["input"], prompt)
    print(f"  Average similarity: {consistency['avgSimilarity']}")
    print(f"  Min similarity: {consistency['minSimilarity']}")
    if consistency["avgSimilarity"] > CONSISTENCY_THRESHOLD:
        print(f"  ✅ Consistent")
    else:
        print(f"  ❌ Low consistency")

if __name__ == "__main__":
    print(f"\n=== EVALUATING {len(ALUMNI_TEST_CASES)} ALUMNI ===\n")

    for alumnus in ALUMNI_TEST_CASES:
        print(f"Evaluating: {json.dumps(alumnus, indent=4)}")
        rating = get_alumnus_rating(alumnus)
        print(json.dumps(rating, indent=4))
        get_evaluation(rating, alumnus, get_alumnus_rating)

    print(f"\n=== EVALUATING {len(STUDENT_TEST_CASES)} STUDENTS ===\n")

    for student in STUDENT_TEST_CASES:
        print(f"Evaluating: {json.dumps(student, indent=4)}")
        rating = get_student_rating(student, new_prompt)
        print(json.dumps(rating, indent=4))
        get_evaluation(rating, student, get_student_rating, new_prompt)