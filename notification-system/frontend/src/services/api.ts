import axios from "axios";
import { Task, TaskListResponse, CreateTaskRequest } from "../types";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: BASE_URL });

export const submitTask = async (data: CreateTaskRequest): Promise<Task> => {
  const res = await api.post<Task>("/tasks", data);
  return res.data;
};

export const fetchTask = async (id: string): Promise<Task> => {
  const res = await api.get<Task>(`/tasks/${id}`);
  return res.data;
};

export const fetchTasks = async (): Promise<TaskListResponse> => {
  const res = await api.get<TaskListResponse>("/tasks");
  return res.data;
};
