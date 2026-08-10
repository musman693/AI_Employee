"use client";

import {
  Archive,
  ArrowLeft,
  AtSign,
  Bell,
  Bot,
  BrainCircuit,
  CalendarClock,
  Check,
  ChevronDown,
  Clock3,
  FileText,
  Inbox,
  LayoutDashboard,
  Mail,
  Menu,
  MessageCircle,
  MoreHorizontal,
  Paperclip,
  Phone,
  Plus,
  Search,
  Send,
  Sparkles,
  Star,
  Users,
  WandSparkles,
  X,
} from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { useInboxThreads, useCreateDraft, useSendReply } from "@/hooks/inbox";

type Channel = "all" | "email" | "whatsapp";
type Conversation = {
  id: number;
  name: string;
  initials: string;
  company: string;
  subject: string;
  preview: string;
  time: string;
  channel: Exclude<Channel, "all">;
  unread?: boolean;
  starred?: boolean;
  priority: "High" | "Normal" | "Low";
  color: string;
};

const conversations: Conversation[] = [
  { id: 1, name: "Sarah Mitchell", initials: "SM", company: "Northstar Studio", subject: "Q3 campaign proposal", preview: "Thanks for sending this over. The direction looks strong — could you clarify the timeline for phase two?", time: "9:42 AM", channel: "email", unread: true, starred: true, priority: "High", color: "#d76748" },
  { id: 2, name: "Omar Farooq", initials: "OF", company: "Crescent Retail", subject: "Order #CR-2841 confirmed", preview: "Perfect, thank you! Please share the invoice here when it’s ready.", time: "9:18 AM", channel: "whatsapp", unread: true, priority: "Normal", color: "#347c6a" },
  { id: 3, name: "Elena Rossi", initials: "ER", company: "Forma Labs", subject: "Re: Partnership discussion", preview: "Thursday at 2 PM works for our team. Looking forward to speaking.", time: "Yesterday", channel: "email", priority: "Normal", color: "#6c71b5" },
  { id: 4, name: "David Chen", initials: "DC", company: "Arcline Systems", subject: "Product availability", preview: "Do you have 40 units in stock? We would need delivery before the 16th.", time: "Yesterday", channel: "whatsapp", priority: "High", color: "#b06f3e" },
  { id: 5, name: "Maya Thompson", initials: "MT", company: "Fieldwork Co.", subject: "Updated brand assets", preview: "I’ve attached the final logo package and usage guidelines for your team.", time: "Mon", channel: "email", priority: "Low", color: "#48769a" },
];

const nav = [
  { label: "Overview", icon: LayoutDashboard, href: "#" },
  { label: "Inbox", icon: Inbox, href: "/inbox", active: true, count: 8 },
  { label: "CRM", icon: Users, href: "/crm" },
  { label: "Finance", icon: FileText, href: "/finance" },
  { label: "Intelligence", icon: BrainCircuit, href: "/intelligence" },
  { label: "Tasks", icon: Check, href: "#" },
];

export function EmailWhatsAppModule() {
  const [channel, setChannel] = useState<Channel>("all");
  const [selectedId, setSelectedId] = useState(1);
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState("");
  const [isDrafting, setIsDrafting] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mobileThread, setMobileThread] = useState(false);

  const { data: threadsFromApi, error: threadsError } = useInboxThreads();
  const { mutateAsync: createDraftApi } = useCreateDraft();
  const sendReplyMutation = useSendReply();

  const conversationState = useMemo<Conversation[]>(() => {
    if (!threadsFromApi?.length) return conversations;
    return threadsFromApi.map((thread, index) => {
      const name = thread.participants?.[0] ?? "Unknown";
      return {
        id: Number(thread.id) || index + 1000,
        name,
        initials: name.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase() || "NA",
        company: "",
        subject: thread.subject || thread.preview || "(no subject)",
        preview: thread.preview || thread.messages?.[0]?.text || "",
        time: thread.messages?.at(-1)?.timestamp || "",
        channel: thread.channel,
        unread: thread.unread,
        priority: thread.priority,
        color: conversations[index % conversations.length].color,
      };
    });
  }, [threadsFromApi]);

  const filtered = useMemo(() => conversationState.filter((item) => {
    const matchesChannel = channel === "all" || item.channel === channel;
    const haystack = `${item.name} ${item.company} ${item.subject}`.toLowerCase();
    return matchesChannel && haystack.includes(query.toLowerCase());
  }), [channel, query, conversationState]);

  const selected = conversationState.find((item) => item.id === selectedId) ?? conversationState[0] ?? conversations[0];

  async function createDraft() {
    setIsDrafting(true);
    try {
      const res = await createDraftApi({ threadId: String(selected.id), subject: selected.subject, prompt: "Please draft a professional reply to the latest message." });
      setDraft(res.draft ?? "");
    } catch (e) {
      console.error(e);
    } finally {
      setIsDrafting(false);
    }
  }

  return (
    <main className="app-frame">
      {sidebarOpen && <button aria-label="Close navigation" className="mobile-scrim" onClick={() => setSidebarOpen(false)} />}
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand"><span className="brand-mark"><Sparkles size={17} /></span><span>workmate</span><button className="icon-button mobile-close" onClick={() => setSidebarOpen(false)}><X size={18} /></button></div>
        <button className="compose-button"><Plus size={17} /> Compose</button>
        <nav className="primary-nav" aria-label="Primary navigation">
          {nav.map(({ label, icon: Icon, href, active, count }) => <Link href={href} key={label} className={active ? "active" : ""}><Icon size={18} /><span>{label}</span>{count && <b>{count}</b>}</Link>)}
        </nav>
        <div className="nav-section"><span>Workspace</span><button><Bot size={18} /> AI employees</button><button><AtSign size={18} /> Integrations</button></div>
        <div className="sidebar-foot"><div className="usage"><div><span>AI requests</span><strong>328 / 500</strong></div><i><em /></i><small>Resets in 12 days</small></div><button className="profile"><span>NK</span><div><strong>Nouman Khan</strong><small>Acme Studio</small></div><MoreHorizontal size={17} /></button></div>
      </aside>

      <section className="workspace">
        {threadsError && <div role="status" style={{ padding: "8px 20px", background: "#fff7e6", color: "#805b16", borderBottom: "1px solid #f0d9a7", fontSize: 12 }}>Inbox backend is unavailable. Showing demo conversations.</div>}
        <header className="topbar"><button className="icon-button menu-button" onClick={() => setSidebarOpen(true)}><Menu size={20} /></button><div><p>Communication</p><h1>Unified inbox</h1></div><div className="top-actions"><button className="status-pill"><i /> All systems operational</button><button className="icon-button"><Search size={18} /></button><button className="icon-button notification"><Bell size={18} /><i /></button></div></header>

        <div className="inbox-grid">
          <section className={`conversation-panel ${mobileThread ? "hide-mobile" : ""}`}>
            <div className="channel-tabs">
              {([ ["all", "All", Inbox], ["email", "Email", Mail], ["whatsapp", "WhatsApp", MessageCircle] ] as const).map(([value, label, Icon]) => <button key={value} onClick={() => setChannel(value)} className={channel === value ? "active" : ""}><Icon size={15} />{label}{value === "all" && <span>8</span>}</button>)}
            </div>
            <label className="search-field"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search conversations" /></label>
            <div className="list-heading"><span>{filtered.length} conversations</span><button>Newest <ChevronDown size={14} /></button></div>
            <div className="conversation-list">
              {filtered.map((item) => <button key={item.id} onClick={() => { setSelectedId(item.id); setMobileThread(true); }} className={`conversation-card ${selected.id === item.id ? "selected" : ""}`}>
                <span className="avatar" style={{ background: item.color }}>{item.initials}</span>
                <span className="conversation-copy"><span className="conversation-meta"><strong>{item.name}</strong><time>{item.time}</time></span><span className="subject-row"><b>{item.subject}</b>{item.channel === "whatsapp" ? <MessageCircle size={13} /> : <Mail size={13} />}</span><span className="preview">{item.preview}</span><span className="tags">{item.priority === "High" && <em className="priority">High priority</em>}<em>{item.company}</em></span></span>
                {item.unread && <i className="unread-dot" />}
              </button>)}
              {filtered.length === 0 && <div className="empty-state"><Search size={24} /><strong>No conversations found</strong><span>Try a different name or channel.</span></div>}
            </div>
          </section>

          <section className={`thread-panel ${mobileThread ? "show-mobile" : ""}`}>
            <div className="thread-head"><button className="icon-button back-button" onClick={() => setMobileThread(false)}><ArrowLeft size={19} /></button><span className="avatar large" style={{ background: selected.color }}>{selected.initials}</span><div><h2>{selected.name}</h2><p>{selected.company} · {selected.channel === "email" ? "Email" : "WhatsApp"}</p></div><div className="thread-actions"><button className="icon-button"><Star size={18} fill={selected.starred ? "#c48b2f" : "none"} color={selected.starred ? "#c48b2f" : "currentColor"} /></button><button className="icon-button"><Archive size={18} /></button><button className="icon-button"><MoreHorizontal size={18} /></button></div></div>
            <div className="thread-body">
              <div className="ai-summary"><div className="ai-icon"><WandSparkles size={18} /></div><div><span>AI conversation brief</span><p>Sarah likes the proposal and needs the phase-two timeline clarified before sharing it with her leadership team.</p></div><button>View details</button></div>
              <div className="date-rule"><span>Today</span></div>
              <article className="message incoming"><div className="message-top"><span className="avatar small" style={{ background: selected.color }}>{selected.initials}</span><div><strong>{selected.name}</strong><span>to me · 9:42 AM</span></div><button><MoreHorizontal size={16} /></button></div><h3>{selected.subject}</h3><p>Hi Nouman,</p><p>Thanks for sending this over. The direction looks strong and the team is excited about the campaign concept.</p><p>Could you clarify the timeline for phase two, especially when creative production begins and how long the rollout will take?</p><p>Best,<br />Sarah</p></article>
              <div className="follow-up"><CalendarClock size={17} /><span><strong>Smart follow-up</strong> suggested for Friday if there’s no reply.</span><button>Set reminder</button></div>
            </div>
            <div className="composer-wrap">
              <div className="composer-toolbar"><button className="active">Reply</button><button>Reply all</button><button>Forward</button><span /><button className="tone"><Sparkles size={14} /> Professional <ChevronDown size={13} /></button></div>
              <div className={`composer ${isDrafting ? "drafting" : ""}`}>
                {isDrafting ? <div className="draft-loader"><span /><span /><span /> AI is preparing a thoughtful reply</div> : <textarea aria-label="Reply message" value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Write a reply, or let AI draft one for you…" />}
                <div className="composer-actions"><div><button className="icon-button"><Paperclip size={17} /></button><button className="ai-draft" onClick={createDraft}><Sparkles size={15} /> Draft with AI</button></div><button className="send-button" disabled={!draft.trim()} onClick={async () => {
                      try {
                        await sendReplyMutation.mutateAsync({ threadId: String(selected.id), payload: { body: draft } });
                        setDraft("");
                      } catch (e) {
                        console.error(e);
                      }
                    }}><Send size={15} /> Send</button></div>
              </div>
              <p className="ai-note"><Sparkles size={12} /> AI suggestions use your company knowledge and conversation context.</p>
            </div>
          </section>

          <aside className="contact-panel"><div className="contact-card"><span className="avatar xl" style={{ background: selected.color }}>{selected.initials}</span><h3>{selected.name}</h3><p>Marketing Director</p><span>{selected.company}</span><div className="contact-buttons"><button><Mail size={15} /> Email</button><button><Phone size={15} /> Call</button></div></div><div className="details"><h4>Contact details</h4><dl><div><dt>Email</dt><dd>sarah@northstar.studio</dd></div><div><dt>Phone</dt><dd>+1 415 555 0182</dd></div><div><dt>Location</dt><dd>San Francisco, CA</dd></div></dl></div><div className="details"><h4>Relationship</h4><div className="health"><span>Strong</span><i><em /></i><b>86%</b></div><p>4 conversations · 2 open deals</p></div><div className="activity"><div><h4>Recent activity</h4><button>View all</button></div><p><span><Mail size={14} /></span><b>Proposal sent</b><time>2 days ago</time></p><p><span><Clock3 size={14} /></span><b>Call completed</b><time>Jun 18</time></p></div></aside>
        </div>
      </section>
    </main>
  );
}
