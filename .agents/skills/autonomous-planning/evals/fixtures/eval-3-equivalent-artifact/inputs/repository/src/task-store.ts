export type TaskStatus = "todo" | "doing" | "done";

export type NewTask = {
  title: string;
  description: string;
  status: TaskStatus;
};

export interface TaskStore {
  createManyInTransaction(teamId: string, tasks: NewTask[]): Promise<void>;
}
