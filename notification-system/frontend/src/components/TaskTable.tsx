import React from "react";
import { Task } from "../types";

interface Props {
  tasks: Task[];
  loading: boolean;
}

const statusColor: Record<string, string> = {
  pending: "#f59e0b",
  processing: "#3b82f6",
  completed: "#10b981",
  failed: "#ef4444",
};

const TaskTable: React.FC<Props> = ({ tasks, loading }) => {
  if (loading) return <p>Loading tasks...</p>;
  if (tasks.length === 0) return <p>No tasks yet.</p>;

  return (
    <div className="table-wrapper">
      <table className="task-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Payload</th>
            <th>Status</th>
            <th>Created</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t.id}>
              <td title={t.id}>{t.id.slice(0, 8)}…</td>
              <td>{t.title}</td>
              <td>{t.payload ?? "—"}</td>
              <td>
                <span
                  className="status-badge"
                  style={{ background: statusColor[t.status] }}
                >
                  {t.status}
                </span>
              </td>
              <td>{new Date(t.created_at).toLocaleString()}</td>
              <td>{new Date(t.updated_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TaskTable;
