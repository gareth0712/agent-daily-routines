import { activityRecords, getRecentUnreadActivity } from "../src/activity-store.js";

const ids = getRecentUnreadActivity(activityRecords).map(({ id }) => id).join(",");
if (ids !== "evt-3,evt-1") {
  throw new Error(`expected evt-3,evt-1, received ${ids || "empty"}`);
}
console.log(`UNREAD_IDS=${ids}`);
