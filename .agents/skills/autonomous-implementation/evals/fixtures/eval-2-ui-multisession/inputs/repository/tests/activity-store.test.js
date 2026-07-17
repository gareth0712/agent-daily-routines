import test from "node:test";
import assert from "node:assert/strict";

import { activityRecords, getRecentUnreadActivity } from "../src/activity-store.js";

test("activity fixture contains read and unread records", () => {
  assert.equal(activityRecords.some(({ read }) => read), true);
  assert.equal(activityRecords.some(({ read }) => !read), true);
});

test("selector is not implemented in the source fixture", () => {
  assert.deepEqual(getRecentUnreadActivity(activityRecords), []);
});
