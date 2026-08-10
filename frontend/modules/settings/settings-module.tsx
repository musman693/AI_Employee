"use client";

import { FormEvent, useEffect, useState } from "react";
import { Check, ExternalLink, LoaderCircle, Mail, MessageCircle, Plus, ShieldCheck, Trash2, Users, X } from "lucide-react";
import { Topbar } from "@/components/shared/topbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Provider = "Gmail" | "Outlook" | "WhatsApp";
type Role = "Administrator" | "Manager" | "Member";
type Profile = { name: string; email: string; company: string; role: Role };
type Member = { id: string; email: string; role: Role; status: "Pending" | "Active" };
type Notice = { tone: "success" | "error"; text: string } | null;

const STORE = "ai-employee.settings.v1";
const defaults = {
  profile: { name: "Nouman Khan", email: "nouman@acmestudio.com", company: "Acme Studio", role: "Administrator" as Role },
  connected: { Gmail: true, Outlook: true, WhatsApp: false } as Record<Provider, boolean>,
  mfa: false,
  members: [] as Member[],
};

export function SettingsModule() {
  const [profile, setProfile] = useState<Profile>(defaults.profile);
  const [connected, setConnected] = useState(defaults.connected);
  const [mfa, setMfa] = useState(false);
  const [members, setMembers] = useState<Member[]>([]);
  const [modal, setModal] = useState<"invite" | "mfa" | "support" | null>(null);
  const [notice, setNotice] = useState<Notice>(null);
  const [saving, setSaving] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORE);
      if (saved) {
        const data = JSON.parse(saved) as typeof defaults;
        setProfile(data.profile ?? defaults.profile);
        setConnected(data.connected ?? defaults.connected);
        setMfa(data.mfa ?? false);
        setMembers(data.members ?? []);
      }
    } catch { /* Ignore invalid legacy browser state. */ }
    setReady(true);
  }, []);

  function persist(next = { profile, connected, mfa, members }) {
    localStorage.setItem(STORE, JSON.stringify(next));
  }

  function flash(text: string, tone: "success" | "error" = "success") {
    setNotice({ text, tone });
    window.setTimeout(() => setNotice(null), 3500);
  }

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    await new Promise((resolve) => window.setTimeout(resolve, 350));
    persist(); setSaving(false); flash("Profile settings saved.");
  }

  function toggleProvider(provider: Provider) {
    const next = { ...connected, [provider]: !connected[provider] };
    setConnected(next); persist({ profile, connected: next, mfa, members });
    flash(`${provider} ${next[provider] ? "connected" : "disconnected"}.`);
  }

  function invite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") ?? "").trim();
    const role = String(form.get("role")) as Role;
    if (members.some((member) => member.email.toLowerCase() === email.toLowerCase())) return flash("That person has already been invited.", "error");
    const next = [...members, { id: crypto.randomUUID(), email, role, status: "Pending" as const }];
    setMembers(next); persist({ profile, connected, mfa, members: next }); setModal(null); flash(`Invitation prepared for ${email}.`);
  }

  function removeMember(id: string) {
    const next = members.filter((member) => member.id !== id);
    setMembers(next); persist({ profile, connected, mfa, members: next }); flash("Team member removed.");
  }

  function enableMfa(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const code = String(new FormData(event.currentTarget).get("code") ?? "");
    if (!/^\d{6}$/.test(code)) return flash("Enter a valid six-digit code.", "error");
    setMfa(true); persist({ profile, connected, mfa: true, members }); setModal(null); flash("Multi-factor authentication enabled.");
  }

  function sendSupport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const subject = encodeURIComponent(String(form.get("subject") ?? "AI Employee support"));
    const body = encodeURIComponent(String(form.get("message") ?? ""));
    window.location.href = `mailto:support@aiemployee.local?subject=${subject}&body=${body}`;
    setModal(null); flash("Your email client has been opened.");
  }

  if (!ready) return <div className="p-8 text-sm text-muted-foreground">Loading settings…</div>;

  return <div className="flex-1 overflow-auto p-6 lg:p-8">
    <Topbar title="Settings" subtitle="Account, security, team, and integrations" />
    {notice && <div role="status" className={`fixed right-6 top-6 z-50 flex items-center gap-2 rounded-xl px-4 py-3 text-sm shadow-xl ${notice.tone === "success" ? "bg-emerald-700 text-white" : "bg-red-700 text-white"}`}><Check className="size-4" />{notice.text}</div>}
    <div className="mx-auto mt-8 grid max-w-6xl gap-6 lg:grid-cols-[1.2fr_.8fr]">
      <div className="space-y-6">
        <Card title="Profile" subtitle="Keep your account and company details current.">
          <form onSubmit={saveProfile} className="grid gap-4 sm:grid-cols-2">
            <Field label="Full name"><Input required value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} /></Field>
            <Field label="Email address"><Input required type="email" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} /></Field>
            <Field label="Company name" wide><Input required value={profile.company} onChange={(e) => setProfile({ ...profile, company: e.target.value })} /></Field>
            <Field label="Your role" wide><select className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm" value={profile.role} onChange={(e) => setProfile({ ...profile, role: e.target.value as Role })}>{roles.map((role) => <option key={role}>{role}</option>)}</select></Field>
            <div className="sm:col-span-2 flex justify-end"><Button disabled={saving}>{saving && <LoaderCircle className="animate-spin" />}{saving ? "Saving…" : "Save changes"}</Button></div>
          </form>
        </Card>
        <Card title="Integrations" subtitle="Connect the channels your AI employee can work in.">
          <div className="space-y-3">{providers.map(({ name, description, icon: Icon }) => <div key={name} className="flex items-center gap-4 rounded-2xl border border-border p-4"><span className="grid size-10 place-items-center rounded-xl bg-muted"><Icon className="size-5" /></span><div className="min-w-0 flex-1"><p className="font-medium">{name}</p><p className="text-sm text-muted-foreground">{description}</p></div><span className={`hidden rounded-full px-2.5 py-1 text-xs sm:block ${connected[name] ? "bg-emerald-100 text-emerald-800" : "bg-muted text-muted-foreground"}`}>{connected[name] ? "Connected" : "Not connected"}</span><Button type="button" size="sm" variant={connected[name] ? "outline" : "default"} onClick={() => toggleProvider(name)}>{connected[name] ? "Disconnect" : "Connect"}</Button></div>)}</div>
        </Card>
        <Card title="Team and permissions" subtitle="Invite teammates and control workspace access." action={<Button size="sm" onClick={() => setModal("invite")}><Plus />Invite</Button>}>
          <div className="space-y-3"><TeamRow email={profile.email} role={profile.role} status="Active" />{members.map((member) => <TeamRow key={member.id} {...member} onRemove={() => removeMember(member.id)} />)}{members.length === 0 && <p className="rounded-xl bg-muted p-4 text-sm text-muted-foreground">No teammates invited yet.</p>}</div>
        </Card>
      </div>
      <aside className="space-y-6">
        <Card title="Security" subtitle="Protect your account with a second verification step.">
          <div className="rounded-2xl border border-border p-4"><div className="flex items-center gap-3"><ShieldCheck className={mfa ? "text-emerald-600" : "text-muted-foreground"} /><div className="flex-1"><p className="font-medium">Multi-factor authentication</p><p className="text-sm text-muted-foreground">{mfa ? "Enabled for this account" : "Not configured"}</p></div></div><Button className="mt-4 w-full" variant={mfa ? "outline" : "default"} onClick={() => mfa ? (setMfa(false), persist({ profile, connected, mfa: false, members }), flash("MFA disabled.")) : setModal("mfa")}>{mfa ? "Disable MFA" : "Configure MFA"}</Button></div>
        </Card>
        <Card title="Support" subtitle="Tell us what is blocking your team."><Button variant="outline" className="w-full" onClick={() => setModal("support")}><ExternalLink />Contact support</Button></Card>
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-900">Settings are saved in this browser until the corresponding backend endpoints are available. OAuth connections and MFA verification must be enforced server-side before production launch.</div>
      </aside>
    </div>
    {modal === "invite" && <Modal title="Invite teammate" close={() => setModal(null)}><form onSubmit={invite} className="space-y-4"><Field label="Work email"><Input name="email" type="email" required autoFocus placeholder="teammate@company.com" /></Field><Field label="Role"><select name="role" className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm">{roles.slice(1).map((role) => <option key={role}>{role}</option>)}</select></Field><ModalActions close={() => setModal(null)} submit="Send invitation" /></form></Modal>}
    {modal === "mfa" && <Modal title="Configure MFA" close={() => setModal(null)}><form onSubmit={enableMfa} className="space-y-4"><div className="rounded-xl bg-muted p-4 text-sm"><p className="font-medium">1. Add AI Employee to your authenticator app.</p><p className="mt-2 font-mono text-xs tracking-widest">AIEE MPLO YEE2 FA7K</p></div><Field label="2. Enter the six-digit verification code"><Input name="code" required inputMode="numeric" pattern="[0-9]{6}" maxLength={6} placeholder="123456" /></Field><ModalActions close={() => setModal(null)} submit="Verify and enable" /></form></Modal>}
    {modal === "support" && <Modal title="Contact support" close={() => setModal(null)}><form onSubmit={sendSupport} className="space-y-4"><Field label="Subject"><Input name="subject" required placeholder="How can we help?" /></Field><label className="grid gap-2 text-sm font-medium">Message<textarea name="message" required className="min-h-28 rounded-lg border border-input bg-transparent p-3 font-normal outline-none" placeholder="Describe the issue…" /></label><ModalActions close={() => setModal(null)} submit="Open email" /></form></Modal>}
  </div>;
}

const roles: Role[] = ["Administrator", "Manager", "Member"];
const providers: Array<{ name: Provider; description: string; icon: typeof Mail }> = [
  { name: "Gmail", description: "Email, drafts, and customer threads", icon: Mail },
  { name: "Outlook", description: "Microsoft mail and calendar", icon: Mail },
  { name: "WhatsApp", description: "Business messages and support", icon: MessageCircle },
];

function Card({ title, subtitle, action, children }: { title: string; subtitle: string; action?: React.ReactNode; children: React.ReactNode }) { return <section className="rounded-2xl border border-border bg-card p-5 shadow-sm"><header className="mb-5 flex items-start justify-between gap-4"><div><h2 className="font-semibold">{title}</h2><p className="mt-1 text-sm text-muted-foreground">{subtitle}</p></div>{action}</header>{children}</section>; }
function Field({ label, wide, children }: { label: string; wide?: boolean; children: React.ReactNode }) { return <label className={`grid gap-2 text-sm font-medium ${wide ? "sm:col-span-2" : ""}`}>{label}{children}</label>; }
function TeamRow({ email, role, status, onRemove }: { email: string; role: Role; status: "Pending" | "Active"; onRemove?: () => void }) { return <div className="flex items-center gap-3 rounded-xl border border-border p-3"><span className="grid size-9 place-items-center rounded-full bg-muted"><Users className="size-4" /></span><div className="min-w-0 flex-1"><p className="truncate text-sm font-medium">{email}</p><p className="text-xs text-muted-foreground">{role} · {status}</p></div>{onRemove && <Button aria-label={`Remove ${email}`} size="icon-sm" variant="ghost" onClick={onRemove}><Trash2 /></Button>}</div>; }
function Modal({ title, close, children }: { title: string; close: () => void; children: React.ReactNode }) { return <div className="fixed inset-0 z-40 grid place-items-center p-4"><button aria-label="Close dialog" className="absolute inset-0 bg-black/45" onClick={close} /><section role="dialog" aria-modal="true" aria-label={title} className="relative w-full max-w-md rounded-2xl bg-card p-6 shadow-2xl"><header className="mb-5 flex items-center justify-between"><h2 className="text-lg font-semibold">{title}</h2><Button size="icon-sm" variant="ghost" onClick={close}><X /></Button></header>{children}</section></div>; }
function ModalActions({ close, submit }: { close: () => void; submit: string }) { return <div className="flex justify-end gap-2 pt-2"><Button type="button" variant="outline" onClick={close}>Cancel</Button><Button type="submit">{submit}</Button></div>; }
