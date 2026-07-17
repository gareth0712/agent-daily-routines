import { searchTasks } from "../src/search.js";

const tasks = [
  { id: 1, title: "Write release notes" },
  { id: 2, title: "Fix Billing Bug" },
  { id: 3, title: "Review billing metrics" },
];

const matches = searchTasks(tasks, "  FIX BILLING BUG  ");
if (matches.length !== 1 || matches[0].id !== 2) {
  throw new Error(`expected task 2, received ${JSON.stringify(matches)}`);
}
console.log("MATCH_IDS=2");
