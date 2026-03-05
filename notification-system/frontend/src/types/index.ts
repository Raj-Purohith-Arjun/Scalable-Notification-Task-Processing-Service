export interface Task {
  id: string;
  title: string;
  payload: string | null;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

export interface CreateTaskRequest {
  title: string;
  payload?: string;
}
