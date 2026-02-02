import { parse } from 'csv-parse/sync';
import "dotenv/config";
import fs from 'fs/promises';
import Groq from "groq-sdk";
import { BUCKETS } from "./buckets.js";

const schema = {}
for (const bucket of BUCKETS) {
  schema[bucket] = { type: "number" };
}

const content = await fs.readFile("students.csv");
const people = parse(content, { bom: true }).flat();

const groq = new Groq();

export async function getStudentRating(person) {
  const response = await groq.chat.completions.create({
    model: "openai/gpt-oss-120b",
    messages: [
      { role: "system", content: `Extract computer science interest information from the following student's interests, disinterests, and what their ideal mentor would look like. Rate the person's interest in each computer science field from -1 to 1, where -1 is very negative and 1 is very positive. If they do not state any interest in a field, rate it as 0.` },
      {
        role: "user",
        content: JSON.stringify(person),
      },
    ],
    response_format: {
      type: "json_schema",
      json_schema: {
        name: "computer_science_interest",
        strict: true,
        schema: {
          type: "object",
          properties: schema,
          required: BUCKETS,
          additionalProperties: false
        }
      }
    },

  });

  return JSON.parse(response.choices[0]?.message?.content || "{}")
}

function shuffle(array) {
  let currentIndex = array.length, randomIndex;

  // While there remain elements to shuffle.
  while (currentIndex != 0) {

    // Pick a remaining element.
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;

    // And swap it with the current element using array destructuring.
    [array[currentIndex], array[randomIndex]] = [
      array[randomIndex], array[currentIndex]];
  }

  console.log(array);
  return array;
}

// const N = 5;
// for (const person of shuffle(people).slice(0, N)) {
//   console.log(await getStudentRating(person));
// }