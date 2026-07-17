export const activityRecords = Object.freeze([
  Object.freeze({ id: "evt-1", label: "Invoice paid", occurredAt: "2026-07-14T08:00:00Z", read: false }),
  Object.freeze({ id: "evt-2", label: "Workspace renamed", occurredAt: "2026-07-14T09:00:00Z", read: true }),
  Object.freeze({ id: "evt-3", label: "New teammate joined", occurredAt: "2026-07-14T10:00:00Z", read: false }),
]);

export function getRecentUnreadActivity() {
  return [];
}
