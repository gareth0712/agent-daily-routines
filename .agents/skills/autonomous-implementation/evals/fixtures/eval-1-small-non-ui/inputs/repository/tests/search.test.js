import test from "node:test";
import assert from "node:assert/strict";

import { searchTasks } from "../src/search.js";

const tasks = [
  { id: 1, title: "Write release notes" },
  { id: 2, title: "Fix Billing Bug" },
  { id: 3, title: "Review billing metrics" },
];

test("keeps matching tasks in input order", () => {
  assert.deepEqual(searchTasks(tasks, "billing").map(({ id }) => id), [3]);
});

test("does not mutate the input list", () => {
  const snapshot = structuredClone(tasks);
  searchTasks(tasks, "release");
  assert.deepEqual(tasks, snapshot);
});
