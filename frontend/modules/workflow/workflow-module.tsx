"use client";

import { FormEvent, useState } from "react";
import { Activity, CheckCircle2, CirclePlay, GitBranch, LoaderCircle, Mail, Plus, Power, Trash2, X } from "lucide-react";
import { useDeleteWorkflow, useExecuteWorkflow, useSaveWorkflow, useUpdateWorkflow, useWorkflows } from "@/hooks/tasks";
import type { WorkflowAction, WorkflowCreate } from "@/types/api";
import styles from "./workflow.module.css";

const triggers = [
  ["customer.created", "Customer created"], ["invoice.paid", "Invoice paid"], ["invoice.overdue", "Invoice overdue"],
  ["task.completed", "Task completed"], ["deal.won", "Deal won"], ["quotation.approved", "Quotation approved"], ["manual", "Manual trigger"],
];
const actionTypes = [["send_email", "Send email"], ["create_task", "Create task"], ["create_followup", "Create follow-up"], ["update_crm", "Update CRM"], ["notify_sales", "Notify sales"], ["webhook", "Call webhook"], ["delay", "Wait / delay"]];

export function WorkflowModule() {
  const workflows = useWorkflows();
  const save = useSaveWorkflow();
  const update = useUpdateWorkflow();
  const remove = useDeleteWorkflow();
  const execute = useExecuteWorkflow();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [trigger, setTrigger] = useState(triggers[0][0]);
  const [actions, setActions] = useState<WorkflowAction[]>([]);
  const [actionType, setActionType] = useState(actionTypes[0][0]);
  const [actionName, setActionName] = useState("");
  const [configValue, setConfigValue] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  function addAction(event: FormEvent) {
    event.preventDefault(); setError("");
    if (!actionName.trim()) return setError("Give the action a clear name.");
    const key = actionType === "send_email" ? "to" : actionType === "webhook" ? "url" : actionType === "delay" ? "seconds" : "value";
    const config = configValue.trim() ? { [key]: actionType === "delay" ? Number(configValue) || 0 : configValue.trim() } : {};
    setActions((current) => [...current, { type: actionType, name: actionName.trim(), config, order: current.length }]);
    setActionName(""); setConfigValue("");
  }

  async function createWorkflow(event: FormEvent) {
    event.preventDefault(); setError("");
    if (!name.trim()) return setError("Workflow name is required.");
    if (!actions.length) return setError("Add at least one action.");
    const payload: WorkflowCreate = { name: name.trim(), description: description.trim() || null, status: "draft", trigger: { type: trigger, conditions: {} }, actions };
    try { await save.mutateAsync(payload); setName(""); setDescription(""); setActions([]); setNotice("Workflow created as a draft."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Workflow could not be created."); }
  }

  async function toggle(id: string, active: boolean) { try { await update.mutateAsync({ id, payload: { status: active ? "inactive" : "active" } }); setNotice(active ? "Workflow paused." : "Workflow activated."); } catch (reason) { setError(reason instanceof Error ? reason.message : "Status could not be updated."); } }
  async function deleteOne(id: string) { try { await remove.mutateAsync(id); setNotice("Workflow deleted."); } catch (reason) { setError(reason instanceof Error ? reason.message : "Workflow could not be deleted."); } }
  async function run(id: string) { try { const result = await execute.mutateAsync(id); setNotice(`Test run ${result.status}.`); } catch (reason) { setError(reason instanceof Error ? reason.message : "Test run failed."); } }

  return <main className={styles.page}>
    <header className={styles.hero}><div><span>Automation studio</span><h1>Workflow builder</h1><p>Connect business events to reliable, repeatable actions.</p></div><div className={styles.heroIcon}><GitBranch /></div></header>
    {(error || workflows.error) && <div className={styles.error}>{error || "Workflow service is unavailable."}<button onClick={() => { setError(""); workflows.refetch(); }}><X /></button></div>}
    {notice && <div className={styles.notice}><CheckCircle2 />{notice}<button onClick={() => setNotice("")}><X /></button></div>}
    <div className={styles.layout}>
      <form className={styles.builder} onSubmit={createWorkflow}>
        <section><div className={styles.sectionTitle}><span>01</span><div><h2>Define the trigger</h2><p>Choose the event that starts this workflow.</p></div></div><div className={styles.grid}><label>Workflow name<input value={name} onChange={(e) => setName(e.target.value)} placeholder="Welcome new customers" /></label><label>Trigger<select value={trigger} onChange={(e) => setTrigger(e.target.value)}>{triggers.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><label className={styles.wide}>Description<textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What should this automation accomplish?" /></label></div></section>
        <section><div className={styles.sectionTitle}><span>02</span><div><h2>Build the action chain</h2><p>Actions run from top to bottom.</p></div></div><div className={styles.actionForm}><label>Action type<select value={actionType} onChange={(e) => setActionType(e.target.value)}>{actionTypes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><label>Action name<input value={actionName} onChange={(e) => setActionName(e.target.value)} placeholder="Send welcome email" /></label><label>Configuration<input value={configValue} onChange={(e) => setConfigValue(e.target.value)} placeholder={actionType === "send_email" ? "Recipient or template variable" : actionType === "webhook" ? "https://…" : actionType === "delay" ? "Seconds" : "Optional value"} /></label><button className={styles.add} onClick={addAction}><Plus />Add action</button></div>
          <div className={styles.chain}>{actions.map((action, index) => <article key={`${action.name}-${index}`}><span>{index + 1}</span><div><b>{action.name}</b><small>{actionTypes.find(([value]) => value === action.type)?.[1]}{Object.keys(action.config).length ? ` · ${Object.values(action.config)[0]}` : ""}</small></div><button type="button" aria-label={`Remove ${action.name}`} onClick={() => setActions((current) => current.filter((_, item) => item !== index))}><Trash2 /></button></article>)}{!actions.length && <div className={styles.empty}>Add the first action to start your automation chain.</div>}</div>
        </section>
        <footer><span>{actions.length} action{actions.length === 1 ? "" : "s"}</span><button disabled={save.isPending}>{save.isPending ? <LoaderCircle className={styles.spin} /> : <GitBranch />}{save.isPending ? "Creating…" : "Create workflow"}</button></footer>
      </form>
      <aside className={styles.library}><div className={styles.libraryHead}><div><span>Workflow library</span><h2>Your automations</h2></div><Activity /></div>{workflows.isLoading ? <div className={styles.loading}><LoaderCircle className={styles.spin} />Loading workflows…</div> : <div className={styles.list}>{(workflows.data ?? []).map((workflow) => <article key={workflow.id}><header><span data-status={workflow.status}>{workflow.status}</span><button aria-label={`Delete ${workflow.name}`} onClick={() => deleteOne(workflow.id)}><Trash2 /></button></header><h3>{workflow.name}</h3><p>{workflow.description || "No description"}</p><div><small>{workflow.trigger.type.replaceAll(".", " ")}</small><small>{workflow.actions.length} actions</small><small>{workflow.execution_count ?? 0} runs</small></div><footer><button onClick={() => toggle(workflow.id, workflow.status === "active")}><Power />{workflow.status === "active" ? "Pause" : "Activate"}</button><button onClick={() => run(workflow.id)}><CirclePlay />Test</button></footer></article>)}{!workflows.data?.length && <div className={styles.empty}>No workflows yet. Build your first automation.</div>}</div>}</aside>
    </div>
  </main>;
}
