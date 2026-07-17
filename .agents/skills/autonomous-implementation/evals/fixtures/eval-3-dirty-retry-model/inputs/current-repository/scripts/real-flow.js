import { notificationsEnabled } from "../src/notify.js";

const actual = notificationsEnabled({ enabled: "false" });
if (actual !== false) {
  throw new Error(`expected false, received ${String(actual)}`);
}
console.log("NOTIFY_FALSE=false");
