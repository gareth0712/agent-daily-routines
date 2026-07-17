import type { TaskStore } from "./task-store";

export type TeamOwner = { userId: string; teamId: string };

export async function requireTeamOwner(): Promise<TeamOwner> {
  throw new Error("fixture boundary");
}
export async function createImportRoute(_store: TaskStore): Promise<void> {
  await requireTeamOwner();
}
