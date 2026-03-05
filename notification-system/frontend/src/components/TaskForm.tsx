import React, { useState } from "react";
import { submitTask } from "../services/api";
import { Task, CreateTaskRequest } from "../types";

interface Props {
  onTaskCreated: (task: Task) => void;
}

const TaskForm: React.FC<Props> = ({ onTaskCreated }) => {
  const [title, setTitle] = useState("");
  const [payload, setPayload] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const req: CreateTaskRequest = { title, payload: payload || undefined };
      const task = await submitTask(req);
      onTaskCreated(task);
      setTitle("");
      setPayload("");
    } catch {
      setError("Failed to submit task");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <h2>Submit Task</h2>
      <div className="field">
        <label>Title</label>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Task title"
          required
        />
      </div>
      <div className="field">
        <label>Payload</label>
        <textarea
          value={payload}
          onChange={(e) => setPayload(e.target.value)}
          placeholder="Optional payload (JSON or text)"
          rows={3}
        />
      </div>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Submit"}
      </button>
    </form>
  );
};

export default TaskForm;
