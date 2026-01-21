import cosineSimilarity from "compute-cosine-similarity";
import "dotenv/config";
import { getAlumniRating } from "./alumni.js";
import { getStudentRating } from "./student.js";
import { BUCKETS } from "./buckets.js";

const schema = {};
for (const bucket of BUCKETS) {
  schema[bucket] = { type: "number" };
}

const ALUMNI_TEST_CASES = [
  {
    input: {
      company: "Datadog",
      role: "Software engineer (distributed systems and query engines)",
      interests: "No preference",
      interestToAvoid: "People obsessed with AI",
      bio: "I am a UCLA alumn working as a Software Engineer at Datadog. I work on distributed query engines and execution. I am excited to help students learn more about the field."
    },
    expectedPos: ["systems_programming", "databases_and_data_management"],
    expectedNeg: ["artificial_intelligence_and_machine_learning"]
  },
  {
    input: {
      company: "Pinterest, UC Berkeley",
      role: "Machine learning engineer (Pinterest Visual Search), lecturer (UC Berkeley, Data Science Undergraduate Studies)",
      interests: "Preferably someone interested in some of the following: software engineering, machine learning / artificial intelligence, computer vision, recommendation systems, research, grad school, industry vs academia, teaching.",
      interestToAvoid: "N/A",
      bio: "Hi! I'm a UCLA alum (Master's in Computer Science, 2016, with focus in AI/ML and computer vision) currently working as a machine learning engineer at Pinterest's Visual Search team. I also teach part-time at UC Berkeley (Data Science Undergraduate Studies program), where I have taught an Intro to Python and an Intro to Deep Learning course. I'm looking forward to help students that are curious about any of the following: AI/ML/computer-vision/recommendation-systems, education, industry vs academia/grad-school, and/or what it's like working in industry! In my free time, I enjoy playing music (piano, bass, guitar, singing), video games, and watching movies (I love Pixar movies, and animation/film in general!)."
    },
    expectedPos: ["artificial_intelligence_and_machine_learning", "education_and_teaching", "research_and_academia"],
    expectedNeg: []
  },
  {
    input: {
      company: "Self-employed (currently on contract with Varda and Relativity)",
      role: "Software Consultant",
      interests: "Prefer students interested in embedded software but this is not a hard requirement.",
      interestToAvoid: "Would like to avoid students solely interested in AI as that's not where my expertise lies.",
      bio: "I'm a UCLA alum who previously worked as a Flight Software Engineer at SpaceX and currently works as a consultant at Varda Space Industries, and Relativity; excited to provide guidance on embedded software development, and the Aerospace & Defense industry."
    },
    expectedPos: ["embedded_systems_and_iot"],
    expectedNeg: ["artificial_intelligence_and_machine_learning"]
  },
  {
    input: {
      company: "Veeva",
      role: "",
      interests: "N/A",
      interestToAvoid: "N/A",
      bio: "I'm a software engineer at Veeva Systems, happy to talk about getting into industry or anything research!"
    },
    expectedPos: ["research_and_academia"],
    expectedNeg: []
  },
  {
    input: {
      company: "intuit",
      role: "Sr. Software Engineer",
      interests: "CS major?",
      interestToAvoid: "n.a",
      bio: "I'm a software engineer at intuit, though i've worked at 10+ companies, startups and had higher level roles, have worked web/backend/android mobile and am happy to chat about anything"
    },
    expectedPos: ["web_development", "backend_development", "mobile_development"],
    expectedNeg: []
  },
]

const STUDENT_TEST_CASES = [
  {
    input: {
      interests: "AI/ML, DevOps, Systems Engineering, Network Engineering, Biotech, Firmware, Hardware",
      disinterests: "Crypto",
      idealMentor: "They would work at any company, whether Big Tech or a startup. They would be knowledgeable in many fields but hopefully at least full-stack. I don't care much about their background, just whether they are able to assist and connect with me."
    },
    expectedPos: ["artificial_intelligence_and_machine_learning", "devops_and_cloud_infrastructure", "systems_programming", "computational_biology", "embedded_systems_and_iot", "computer_hardware_and_architecture"],
    expectedNeg: ["cryptocurrency_and_blockchain"]
  },
  {
    input: {
      interests: "Backend and infrastructure engineering, with a focus on scalable systems, APIs, and data pipelines. Interested in developer platforms, reliability, and performance critical services. Enjoy building tools that support large numbers of users and enable other engineers to move faster.",
      disinterests: "N/A",
      idealMentor: "I’m looking for mentorship on navigating the path to big tech roles, including technical interview preparation and long term career positioning. I’d also value guidance on planning coursework strategically and weighing the tradeoffs between industry experience and pursuing graduate school."
    },
    expectedPos: ["backend_development", "databases_and_data_management"],
    expectedNeg: []
  },
  {
    input: {
      interests: "Mobile/iOS development, game development",
      disinterests: "Operating systems, compilers, anything to do with hardware/memory",
      idealMentor: "Someone from a game development company like Blizzard, etc., expert in developing games and increasing performance"
    },
    expectedPos: ["mobile_development", "game_development"],
    expectedNeg: ["systems_programming", "computer_hardware_and_architecture"]
  },
]

const EXPECTED_POS_THRESHOLD = 0.25; // positive interests should be at least 0.25
const EXPECTED_NEG_THRESHOLD = -0.25; // negative interests should be at most -0.25
const CONSISTENCY_RUNS = 3; // number of runs to test consistency
const CONSISTENCY_THRESHOLD = 0.75; // consistency should be at least 0.75

function validateRating(rating) {
  const errors = [];

  for (const bucket of BUCKETS) {
    if (!(bucket in rating)) {
      errors.push(`Missing bucket: ${bucket}`);
    } else if (typeof rating[bucket] !== 'number') {
      errors.push(`Invalid type for ${bucket}: expected number, got ${typeof rating[bucket]}`);
    } else if (rating[bucket] < -1 || rating[bucket] > 1) {
      errors.push(`Value out of range for ${bucket}: ${rating[bucket]} (expected -1 to 1)`);
    }
  }

  const extraKeys = Object.keys(rating).filter(key => !BUCKETS.includes(key));
  if (extraKeys.length) {
    errors.push(`Extra properties found: ${extraKeys.join(', ')}`);
  }

  return errors;
}

function checkReasonableness(rating, expectedPos, expectedNeg) {
  const issues = [];

  for (const bucket of expectedPos) {
    if (rating[bucket] < EXPECTED_POS_THRESHOLD) {
      issues.push(`Expected high rating for ${bucket}, got ${rating[bucket]}`);
    }
  }

  for (const bucket of expectedNeg) {
    if (rating[bucket] > EXPECTED_NEG_THRESHOLD) {
      issues.push(`Expected low rating for ${bucket}, got ${rating[bucket]}`);
    }
  }

  // const extraBuckets = Object.keys(rating).filter(key => !expectedPos.includes(key) && !expectedNeg.includes(key));
  // for (const bucket of extraBuckets) {
  //   if (rating[bucket] !== 0) {
  //     issues.push(`Expected no rating for ${bucket}, got ${rating[bucket]}`);
  //   }
  // }

  return issues;
}

async function testConsistency(ratingFn, input) {
  const results = [];

  for (let i = 0; i < CONSISTENCY_RUNS; i++) {
    const rating = await ratingFn(input);
    results.push(Object.values(rating));
  }

  const similarities = [];

  for (let i = 0; i < results.length; i++) {
    for (let j = i + 1; j < results.length; j++) {
      similarities.push(cosineSimilarity(results[i], results[j]));
    }
  }

  const avgSimilarity = similarities.reduce((a, b) => a + b, 0) / similarities.length;
  const minSimilarity = Math.min(...similarities);

  return {
    avgSimilarity,
    minSimilarity,
  };
}

async function evaluateAlumni() {
  console.log("\n=== EVALUATING ALUMNI RATING SYSTEM ===\n");

  const results = [];

  let i = 1;
  for (const testCase of ALUMNI_TEST_CASES) {
    console.log(`Test ${i}: ${JSON.stringify(testCase)}`);

    const rating = await getAlumniRating(testCase.input);
    const errors = validateRating(rating);

    if (errors.length) {
      console.log(`  ❌ Errors: ${errors.join(', ')}`);
    } else {
      console.log(`  ✅ Valid`);
    }

    const reasonablenessIssues = checkReasonableness(rating, testCase.expectedPos, testCase.expectedNeg);
    if (reasonablenessIssues.length) {
      console.log(`  ❌ Reasonableness issues: ${reasonablenessIssues.join(', ')}`);
    } else {
      console.log(`  ✅ Reasonable ratings`);
    }

    console.log(`  Testing consistency (${CONSISTENCY_RUNS} runs)...`);
    const consistency = await testConsistency(getAlumniRating, testCase.input);
    console.log(`  Average similarity: ${consistency.avgSimilarity}`);
    console.log(`  Min similarity: ${consistency.minSimilarity}`);
    if (consistency.avgSimilarity > CONSISTENCY_THRESHOLD) {
      console.log(`  ✅ Consistent`);
    } else {
      console.log(`  ❌ Low consistency`);
    }

    results.push(rating);
    console.log(rating);
    console.log();

    i++;
  }
}

async function evaluateStudent() {
  console.log("\n=== EVALUATING STUDENT RATING SYSTEM ===\n");

  const results = [];

  let i = 1;
  for (const testCase of STUDENT_TEST_CASES) {
    console.log(`Test ${i}: ${JSON.stringify(testCase)}`);

    const rating = await getStudentRating(testCase.input);
    const errors = validateRating(rating);

    if (errors.length) {
      console.log(`  ❌ Errors: ${errors.join(', ')}`);
    } else {
      console.log(`  ✅ Valid`);
    }

    const reasonablenessIssues = checkReasonableness(rating, testCase.expectedPos, testCase.expectedNeg);
    if (reasonablenessIssues.length) {
      console.log(`  ❌ Reasonableness issues: ${reasonablenessIssues.join(', ')}`);
    } else {
      console.log(`  ✅ Reasonable ratings`);
    }

    console.log(`  Testing consistency (${CONSISTENCY_RUNS} runs)...`);
    const consistency = await testConsistency(getStudentRating, testCase.input);
    console.log(`  Average similarity: ${consistency.avgSimilarity}`);
    console.log(`  Min similarity: ${consistency.minSimilarity}`);
    if (consistency.avgSimilarity > CONSISTENCY_THRESHOLD) {
      console.log(`  ✅ Consistent`);
    } else {
      console.log(`  ❌ Low consistency`);
    }

    results.push(rating);
    console.log(rating);
    console.log();

    i++;
  }
}

async function main() {
  // await evaluateAlumni();
  await evaluateStudent();

  console.log("\n=== EVALUATION COMPLETE ===\n");
}

main();