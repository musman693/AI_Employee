"use client";

import Link from "next/link";
import { ChangeEvent, DragEvent, FormEvent, useRef, useState } from "react";
import {
  AlertCircle, ArrowRight, AtSign, Bell, Bot, BrainCircuit, Check, CheckCircle2,
  ChevronDown, Clock3, FileAudio, FileCheck2, FileSearch, FileText, Gavel, Inbox,
  LayoutDashboard, LoaderCircle, Menu, MessageSquareText, Mic2, MoreHorizontal,
  Plus, Search, ShieldAlert, Sparkles, UploadCloud, Users, WandSparkles, X,
} from "lucide-react";
import { intelligenceApi } from "./intelligence-api";
import type { ContractAnalysis, DocumentUpload, MeetingAnalysis, SearchResult } from "./intelligence-types";
import styles from "./intelligence.module.css";

type Tab = "meetings" | "documents" | "legal";
type Busy = "meeting" | "document" | "search" | "legal" | "";

const nav = [
  { label: "Overview", icon: LayoutDashboard, href: "#" }, { label: "Inbox", icon: Inbox, href: "/inbox" },
  { label: "CRM", icon: Users, href: "/crm" }, { label: "Finance", icon: FileText, href: "/finance" },
  { label: "Intelligence", icon: BrainCircuit, href: "/intelligence", active: true }, { label: "Tasks", icon: Check, href: "#" },
];

export function IntelligenceModule() {
  const [tab, setTab] = useState<Tab>("meetings");
  const [busy, setBusy] = useState<Busy>("");
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [meeting, setMeeting] = useState<MeetingAnalysis | null>(null);
  const [meetingFile, setMeetingFile] = useState<File | null>(null);
  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [document, setDocument] = useState<DocumentUpload | null>(null);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searched, setSearched] = useState(false);
  const [contract, setContract] = useState<ContractAnalysis | null>(null);

  function changeTab(next: Tab) { setTab(next); setError(""); }
  async function processMeeting() { if (!meetingFile) return; setBusy("meeting"); setError(""); setMeeting(null); try { const response = await intelligenceApi.processMeeting(meetingFile); setMeeting(response.data); } catch (caught) { setError(message(caught)); } finally { setBusy(""); } }
  async function processDocument() { if (!documentFile) return; setBusy("document"); setError(""); setDocument(null); try { setDocument(await intelligenceApi.uploadDocument(documentFile)); } catch (caught) { setError(message(caught)); } finally { setBusy(""); } }
  async function searchDocuments(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const data = new FormData(event.currentTarget); setBusy("search"); setError(""); setSearched(true); try { const response = await intelligenceApi.searchDocuments(String(data.get("query"))); setResults(response.results); } catch (caught) { setError(message(caught)); } finally { setBusy(""); } }
  async function analyzeContract(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const data = new FormData(event.currentTarget); setBusy("legal"); setError(""); setContract(null); try { const response = await intelligenceApi.analyzeContract(String(data.get("contract"))); setContract(response.analysis); } catch (caught) { setError(message(caught)); } finally { setBusy(""); } }

  return <main className={styles.frame}>
    {sidebarOpen && <button className={styles.scrim} aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}
    <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : ""}`}><div className={styles.brand}><span><Sparkles size={17} /></span><b>workmate</b><button onClick={() => setSidebarOpen(false)}><X size={18} /></button></div><button className={styles.quickAdd} onClick={() => changeTab("documents")}><Plus size={17} />Upload document</button><nav className={styles.nav}>{nav.map(({ label, icon: Icon, href, active }) => <Link key={label} href={href} className={active ? styles.active : ""}><Icon size={18} />{label}</Link>)}</nav><div className={styles.navGroup}><span>Workspace</span><Link href="#"><Bot size={18} />AI employees</Link><Link href="#"><AtSign size={18} />Integrations</Link></div><div className={styles.sideFoot}><div className={styles.aiUsage}><div><span>AI requests</span><b>328 / 500</b></div><i><em /></i><small>Resets in 12 days</small></div><div className={styles.profile}><span>NK</span><div><b>Nouman Khan</b><small>Acme Studio</small></div><MoreHorizontal size={17} /></div></div></aside>
    <section className={styles.workspace}><header className={styles.topbar}><button className={styles.menu} onClick={() => setSidebarOpen(true)}><Menu size={20} /></button><div><p>Knowledge workspace</p><h1>Meeting & document intelligence</h1></div><div className={styles.topActions}><button className={styles.status}><i />AI services connected</button><button><Bell size={18} /><i /></button></div></header>
      <div className={styles.content}><section className={styles.hero}><div><span>AI intelligence</span><h2>Turn conversations and documents into decisions.</h2><p>Capture meetings, search company knowledge, and surface legal risks in minutes.</p></div><div className={styles.orbit}><span><BrainCircuit size={23} /></span><i /><i /><i /></div></section>
        <nav className={styles.tabs}><button className={tab === "meetings" ? styles.tabActive : ""} onClick={() => changeTab("meetings")}><Mic2 size={16} /><span>Meeting assistant<small>Transcribe & summarize</small></span></button><button className={tab === "documents" ? styles.tabActive : ""} onClick={() => changeTab("documents")}><FileSearch size={16} /><span>Document intelligence<small>OCR & semantic search</small></span></button><button className={tab === "legal" ? styles.tabActive : ""} onClick={() => changeTab("legal")}><Gavel size={16} /><span>Legal assistant<small>Contract risk analysis</small></span></button></nav>
        {error && <div className={styles.error}><AlertCircle size={18} /><div><b>The backend could not complete this request</b><p>{error}</p></div><button onClick={() => setError("")}><X size={15} /></button></div>}
        {tab === "meetings" ? <Meetings file={meetingFile} setFile={setMeetingFile} process={processMeeting} busy={busy === "meeting"} result={meeting} /> : tab === "documents" ? <Documents file={documentFile} setFile={setDocumentFile} process={processDocument} busy={busy} upload={document} search={searchDocuments} results={results} searched={searched} /> : <Legal busy={busy === "legal"} result={contract} analyze={analyzeContract} />}
      </div>
    </section>
  </main>;
}

function Meetings({ file, setFile, process, busy, result }: { file: File | null; setFile: (file: File | null) => void; process: () => void; busy: boolean; result: MeetingAnalysis | null }) {
  return <section className={styles.moduleGrid}><div><UploadZone kind="meeting" file={file} setFile={setFile} accept=".mp3,.wav,.m4a,.mp4" />{file && !busy && !result && <button className={styles.processButton} onClick={process}><Sparkles size={15} />Transcribe and analyze<ArrowRight size={15} /></button>}{busy && <Processing title="Listening to your meeting" steps={["Secure upload", "Whisper transcription", "Speaker analysis", "Summary & actions"]} />}{result && <MeetingResult result={result} />}</div><aside className={styles.guide}><span><Mic2 size={18} /></span><h3>Meeting intelligence</h3><p>Your recording is transcribed and structured into the information your team needs next.</p><ul><li><Check size={13} />Full searchable transcript</li><li><Check size={13} />Concise executive summary</li><li><Check size={13} />Action items and owners</li><li><Check size={13} />Deadlines and speakers</li></ul><div><ShieldAlert size={15} /><p>Recordings are sent directly to your configured S3 and AI services.</p></div></aside></section>;
}

function Documents({ file, setFile, process, busy, upload, search, results, searched }: { file: File | null; setFile: (file: File | null) => void; process: () => void; busy: Busy; upload: DocumentUpload | null; search: (e: FormEvent<HTMLFormElement>) => void; results: SearchResult[]; searched: boolean }) {
  return <section className={styles.documentLayout}><div className={styles.documentUpload}><div className={styles.sectionHead}><div><span>Knowledge ingestion</span><h3>Add a document</h3></div><FileText size={19} /></div><UploadZone kind="document" file={file} setFile={setFile} accept="image/png,image/jpeg,.png,.jpg,.jpeg" compact />{file && busy !== "document" && !upload && <button className={styles.processButton} onClick={process}><UploadCloud size={15} />Extract and index<ArrowRight size={15} /></button>}{busy === "document" && <Processing title="Reading your document" steps={["Secure upload", "OCR extraction", "Search indexing"]} />}{upload && <div className={styles.uploadSuccess}><CheckCircle2 size={19} /><div><b>Document indexed</b><p>{upload.extracted_snippet || "Text extracted successfully."}</p><small>ID: {upload.document_id}</small></div></div>}</div><div className={styles.searchWorkspace}><div className={styles.sectionHead}><div><span>Company knowledge</span><h3>Search your documents</h3></div><WandSparkles size={19} /></div><form className={styles.knowledgeSearch} onSubmit={search}><Search size={17} /><input name="query" required placeholder="Ask about policies, contracts, or uploaded documents…" /><button disabled={busy === "search"}>{busy === "search" ? <LoaderCircle className={styles.spin} size={15} /> : "Search"}</button></form><div className={styles.results}>{results.map((result) => <article key={result.document_id}><span><FileCheck2 size={17} /></span><div><b>{result.filename}</b><p>{result.content}</p><small>Document ID · {result.document_id.slice(0, 8)}</small></div><button><ArrowRight size={15} /></button></article>)}{searched && busy !== "search" && results.length === 0 && <div className={styles.noResults}><FileSearch size={23} /><b>No matching documents</b><p>Try broader terms or upload a relevant document first.</p></div>}{!searched && <div className={styles.searchPrompt}><div><Sparkles size={20} /></div><b>Search across everything your company knows</b><p>OCR-indexed documents will appear here with their most relevant passages.</p></div>}</div></div></section>;
}

function Legal({ busy, result, analyze }: { busy: boolean; result: ContractAnalysis | null; analyze: (e: FormEvent<HTMLFormElement>) => void }) {
  const sample = "This Agreement automatically renews for successive twelve-month terms. Either party may terminate only with 90 days written notice. The Client shall indemnify and hold harmless the Provider from all claims, losses, and liabilities without limitation.";
  return <section className={styles.legalGrid}><form className={styles.contractInput} onSubmit={analyze}><div className={styles.sectionHead}><div><span>AI legal assistant</span><h3>Analyze contract language</h3></div><Gavel size={19} /></div><label><span>Contract text</span><textarea name="contract" required defaultValue={sample} placeholder="Paste the agreement or clause you want to review…" /></label><footer><p><ShieldAlert size={13} />AI analysis supports—but does not replace—legal advice.</p><button disabled={busy}>{busy ? <LoaderCircle className={styles.spin} size={15} /> : <Sparkles size={15} />}{busy ? "Analyzing…" : "Analyze risk"}</button></footer></form><div className={styles.legalResult}>{busy ? <Processing title="Reviewing contract risk" steps={["Reading clauses", "Identifying obligations", "Scoring risk", "Writing summary"]} /> : result ? <><div className={styles.riskHead}><span data-risk={result.risk_level}>{result.risk_level} risk</span><small>AI contract assessment</small></div><h3>Executive summary</h3><p>{result.summary}</p><h3>Clauses requiring attention</h3><div className={styles.riskList}>{result.risky_clauses.map((clause, index) => <div key={`${clause}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><p>{clause}</p></div>)}</div></> : <div className={styles.legalEmpty}><span><Gavel size={23} /></span><h3>Your risk report will appear here</h3><p>The assistant will identify risky clauses, assign an overall risk level, and prepare an executive summary.</p><div><i /><i /><i /></div></div>}</div></section>;
}

function UploadZone({ kind, file, setFile, accept, compact }: { kind: "meeting" | "document"; file: File | null; setFile: (file: File | null) => void; accept: string; compact?: boolean }) {
  const input = useRef<HTMLInputElement>(null); const [dragging, setDragging] = useState(false);
  function select(event: ChangeEvent<HTMLInputElement>) { setFile(event.target.files?.[0] ?? null); }
  function drop(event: DragEvent) { event.preventDefault(); setDragging(false); setFile(event.dataTransfer.files?.[0] ?? null); }
  return <div className={`${styles.dropzone} ${compact ? styles.compact : ""} ${dragging ? styles.dragging : ""}`} onDragOver={(e) => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={drop}>{file ? <div className={styles.fileSelected}><span>{kind === "meeting" ? <FileAudio size={22} /> : <FileText size={22} />}</span><div><b>{file.name}</b><p>{formatBytes(file.size)} · Ready to process</p></div><button onClick={() => setFile(null)}><X size={16} /></button></div> : <><span className={styles.uploadIcon}><UploadCloud size={24} /></span><h3>Drop your {kind === "meeting" ? "recording" : "document"} here</h3><p>{kind === "meeting" ? "MP3, WAV, M4A or MP4" : "PNG or JPG image for OCR"}</p><button onClick={() => input.current?.click()}>Browse files</button></>}<input ref={input} hidden type="file" accept={accept} onChange={select} /></div>;
}

function Processing({ title, steps }: { title: string; steps: string[] }) { return <div className={styles.processing}><div className={styles.processingOrb}><BrainCircuit size={23} /><i /><i /></div><h3>{title}</h3><p>This may take a moment. Keep this page open.</p><div>{steps.map((step, index) => <span key={step} style={{ animationDelay: `${index * .35}s` }}><i>{index + 1}</i>{step}</span>)}</div></div>; }
function MeetingResult({ result }: { result: MeetingAnalysis }) { return <div className={styles.meetingResult}><div className={styles.resultHero}><span><CheckCircle2 size={19} /></span><div><b>Meeting processed successfully</b><p>{result.speakers.length} speakers · {result.action_items.length} action items · {result.deadlines.length} deadlines</p></div></div><section><span>AI summary</span><p>{result.summary}</p></section><div className={styles.resultColumns}><section><span>Action items</span>{result.action_items.map((item, index) => <div className={styles.actionItem} key={index}><i><Check size={12} /></i><p>{typeof item === "string" ? item : `${item.task ?? "Action"}${item.assignee ? ` — ${item.assignee}` : ""}`}</p></div>)}</section><section><span>Deadlines</span>{result.deadlines.map((deadline, index) => <div className={styles.deadline} key={index}><Clock3 size={14} /><p>{deadline}</p></div>)}</section></div><details><summary><MessageSquareText size={15} />View full transcript<ChevronDown size={15} /></summary><p>{result.raw_transcript}</p></details></div>; }
function message(error: unknown) { return error instanceof Error ? error.message : "Unexpected backend error."; }
function formatBytes(bytes: number) { return bytes < 1_000_000 ? `${Math.max(1, Math.round(bytes / 1000))} KB` : `${(bytes / 1_000_000).toFixed(1)} MB`; }
