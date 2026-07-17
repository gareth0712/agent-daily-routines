import test from "node:test";
import assert from "node:assert/strict";

import { notificationsEnabled } from "../src/notify.js";

test("preserves exact booleans", () => {
  assert.equal(notificationsEnabled({ enabled: true }), true);
  assert.equal(notificationsEnabled({ enabled: false }), false);
});

test("parses trimmed case-insensitive true and false strings", () => {
  assert.equal(notificationsEnabled({ enabled: " TRUE " }), true);
  assert.equal(notificationsEnabled({ enabled: " false " }), false);
});

test("fails closed for absent or unsupported values", () => {
  assert.equal(notificationsEnabled({}), false);
  assert.equal(notificationsEnabled({ enabled: "yes" }), false);
  assert.equal(notificationsEnabled({ enabled: 1 }), false);
});
