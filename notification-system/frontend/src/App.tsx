import React, { useCallback, useEffect, useState } from "react";
import TaskForm from "./components/TaskForm";
import TaskTable from "./components/TaskTable";
import { fetchTasks } from "./services/api";
import { Task } from "./types";
import "./App.css";

const POLL_INTERVAL = 5000;

const App: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTasks = useCallback(async () => {
    try {
      const data = await fetchTasks();
      setTasks(data.tasks);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
    // poll updates
    const id = setInterval(loadTasks, POLL_INTERVAL);
    return () => clearInterval(id);
  }, [loadTasks]);

  const handleCreated = (task: Task) => {
    setTasks((prev) => [task, ...prev]);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Scalable Notification & Task Processing</h1>
      </header>
      <main className="app-main">
        <TaskForm onTaskCreated={handleCreated} />
        <section className="tasks-section">
          <div className="section-header">
            <h2>Tasks</h2>
            <button onClick={loadTasks} className="refresh-btn">
              Refresh
            </button>
          </div>
          <TaskTable tasks={tasks} loading={loading} />
        </section>
      </main>
    </div>
  );
};

export default App;
