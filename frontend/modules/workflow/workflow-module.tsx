"use client";

import { useState } from "react";
import { useWorkflows, useSaveWorkflow } from "@/hooks/tasks";

const TRIGGERS = [
  { value: "on_create", label: "On Create (generic)" },
  { value: "on_lead_created", label: "When Lead Created" },
  { value: "on_invoice_paid", label: "When Invoice Paid" },
  { value: "scheduled", label: "Scheduled" },
];

const ACTION_TYPES = [
  { value: "send_email", label: "Send Email" },
  { value: "create_task", label: "Create Task" },
  { value: "add_tag", label: "Add Tag" },
];

export function WorkflowModule() {
  const { data: workflows, isLoading } = useWorkflows();
  const save = useSaveWorkflow();
  const [name, setName] = useState("");
  const [trigger, setTrigger] = useState(TRIGGERS[0].value);
  const [actions, setActions] = useState<Array<any>>([]);
  const [newActionType, setNewActionType] = useState(ACTION_TYPES[0].value);
  const [newActionPayload, setNewActionPayload] = useState("{}");

  async function create() {
    if (!name.trim()) return;
    try {
      const payloadActions = actions.map((a, i) => ({ ...a, id: a.id ?? `a-${Date.now()}-${i}` }));
      await save.mutateAsync({ id: `wf-${Date.now()}`, name, trigger, actions: payloadActions });
      setName("");
      setActions([]);
    } catch (e) {
      console.error(e);
    }
  }

  function addAction() {
    try {
      const parsed = JSON.parse(newActionPayload || "{}");
      setActions((s) => [...s, { type: newActionType, payload: parsed }]);
      setNewActionPayload("{}");
    } catch (e) {
      // keep simple: fallback to raw string
      setActions((s) => [...s, { type: newActionType, payload: newActionPayload }]);
      setNewActionPayload("{}");
    }
  }

  function removeAction(index: number) {
    setActions((s) => s.filter((_, i) => i !== index));
  }

  if (isLoading) return <div>Loading workflows…</div>;

  return (
    <div>
      <h2>Workflow Builder</h2>
      <p>Create automation workflows to run on triggers such as new leads, invoices, or completed tasks.</p>
      <div style={{ marginTop: 12 }}>
        <input placeholder="Workflow name" value={name} onChange={(e) => setName(e.target.value)} />
        <select value={trigger} onChange={(e) => setTrigger(e.target.value)} style={{ marginLeft: 8 }}>
          {TRIGGERS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
        <button onClick={create} style={{ marginLeft: 8 }}>Create</button>
      </div>

      <div style={{ marginTop: 16, borderTop: "1px solid #eee", paddingTop: 12 }}>
        <h3>Actions</h3>
        <div>
          <select value={newActionType} onChange={(e) => setNewActionType(e.target.value)}>
            {ACTION_TYPES.map((a) => <option key={a.value} value={a.value}>{a.label}</option>)}
          </select>
          <textarea placeholder='{"to":"me@example.com","subject":"Hi"}' value={newActionPayload} onChange={(e) => setNewActionPayload(e.target.value)} style={{ width: 400, height: 80, marginLeft: 8 }} />
        </div>
        <div style={{ marginTop: 8 }}>
          <button onClick={addAction}>Add Action</button>
        </div>
        <ul style={{ marginTop: 12 }}>
          {actions.map((a, i) => (
            <li key={i} style={{ marginBottom: 6 }}>
              <strong>{a.type}</strong> — <code style={{ background: "#f6f6f6", padding: "2px 6px" }}>{typeof a.payload === "string" ? a.payload : JSON.stringify(a.payload)}</code>
              <button onClick={() => removeAction(i)} style={{ marginLeft: 8 }}>Remove</button>
            </li>
          ))}
        </ul>
      </div>

      <ul style={{ marginTop: 16 }}>
        {(workflows ?? []).map((wf: any) => (
          <li key={wf.id} style={{ marginBottom: 8 }}>
            <strong>{wf.name}</strong> — trigger: {wf.trigger} — actions: {(wf.actions || []).length}
          </li>
        ))}
      </ul>
    </div>
  );
}
