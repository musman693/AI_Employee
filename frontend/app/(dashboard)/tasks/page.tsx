"use client";

import { useMemo, useState } from "react";
import { useTasks, useUpdateTask } from "@/hooks/tasks";
import styles from "./tasks.module.css";

export default function TasksPage() {
  const { data: tasks, isLoading, error } = useTasks();
  const updateMutation = useUpdateTask();
  const [dragged, setDragged] = useState<string | null>(null);

  const columns = useMemo(() => ({
    todo: [] as any[],
    in_progress: [] as any[],
    done: [] as any[],
  }), []);

  if (tasks) tasks.forEach((t: any) => { (columns[t.status as keyof typeof columns] ?? columns.todo).push(t); });

  async function changeStatus(taskId: string, status: string) {
    try { await updateMutation.mutateAsync({ taskId, payload: { status } }); }
    catch (e) { console.error(e); }
  }

  if (isLoading) return <div className={styles.loading}>Loading tasks…</div>;
  if (error) return <div className={styles.error}>Could not load tasks</div>;

  return (
    <main className={styles.frame}>
      <header className={styles.head}><div><p>Work management</p><h1>Tasks</h1></div></header>
      <section className={styles.board}>
        {(["todo", "in_progress", "done"] as const).map((col) => (
          <div key={col} className={styles.column} onDragOver={(e) => e.preventDefault()} onDrop={async (e) => {
            e.preventDefault(); const id = e.dataTransfer.getData("text/task"); if (!id) return; await changeStatus(id, col.replace("_", "_") ); setDragged(null);
          }}>
            <h3>{col === "todo" ? "To do" : col === "in_progress" ? "In progress" : "Done"}</h3>
            <div className={styles.cards}>
              {(columns as any)[col].map((task: any) => (
                <article key={task.id} draggable onDragStart={(e) => e.dataTransfer.setData("text/task", String(task.id))} className={styles.card}>
                  <div className={styles.cardTop}><strong>{task.title}</strong><span className={styles.priority}>{task.priority ?? ""}</span></div>
                  <div className={styles.meta}><small>{task.assignee ?? "—"}</small><small>{task.due_date ? new Date(task.due_date).toLocaleDateString() : "No due"}</small></div>
                  <div className={styles.actions}><button onClick={() => void changeStatus(String(task.id), col === "done" ? "in_progress" : "done")}>{col === "done" ? "Reopen" : "Mark done"}</button></div>
                </article>
              ))}
            </div>
          </div>
        ))}
      </section>
    </main>
  );
}
