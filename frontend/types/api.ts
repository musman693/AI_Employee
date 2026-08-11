export type SignInPayload = {
  email: string;
  password: string;
};

export type SignUpPayload = {
  name: string;
  email: string;
  password: string;
};

export type UserProfile = {
  id: string;
  name: string;
  email: string;
  role: string;
  company: string;
  integrations: Array<{ provider: string; connected: boolean }>;
};

export type Customer = {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string;
  status: string;
  value: number;
  next_step: string;
};

export type Lead = {
  id: number;
  name: string;
  company: string | null;
  email: string | null;
  source: string | null;
  status: string;
  score: number | null;
  assigned_to: string | null;
  converted_customer_id: number | null;
  created_at: string;
  updated_at: string;
};

export type LeadCreate = Pick<Lead, "name"> & Partial<Pick<Lead, "company" | "email" | "source" | "status" | "score" | "assigned_to">>;

export type Deal = {
  id: string;
  customer_id: string;
  title: string;
  stage: string;
  value: number;
  probability: number;
  close_date: string;
};

export type Invoice = {
  id: string;
  invoice_number: string;
  client_name: string;
  client_email: string;
  due_date: string;
  total: number;
  status: string;
  payment_link?: string;
};

export type Quotation = {
  id: string;
  client_name: string;
  client_email: string;
  payment_terms: string;
  created_at: string;
  total: number;
  status: string;
};

export type FinanceSummary = {
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  profit_margin_percent: number;
  outstanding_invoices: number;
  ai_insight: string;
};

export type Forecast = {
  projected_revenue: number;
  projected_profit: number;
  confidence_percent: number;
  ai_analysis: string;
  recommendations: string[];
};

export type CategorizationRequest = {
  description: string;
  amount: number;
};

export type CategorizationResult = {
  suggested_category: string;
  confidence_percent: number;
  ai_reasoning: string;
};

export type ConversationMessage = {
  id: string;
  sender: string;
  text: string;
  timestamp: string;
  type: "email" | "whatsapp";
};

export type ConversationThread = {
  id: string;
  subject: string;
  participants: string[];
  preview: string;
  channel: "email" | "whatsapp";
  unread: boolean;
  priority: "High" | "Normal" | "Low";
  tags: string[];
  messages: ConversationMessage[];
};

export type ThreadReply = {
  body: string;
  draft_only?: boolean;
};

export type DraftRequest = {
  threadId: string;
  subject: string;
  prompt: string;
};

export type MeetingAnalysis = {
  id: string;
  title: string;
  summary: string;
  speakers: string[];
  action_items: Array<{ task: string; assignee?: string }>;
  deadlines: string[];
  raw_transcript: string;
};

export type DocumentUpload = {
  document_id: string;
  filename: string;
  extracted_snippet: string;
  ocr_status: string;
};

export type SearchResult = {
  document_id: string;
  filename: string;
  content: string;
};

export type ContractAnalysis = {
  risk_level: string;
  summary: string;
  risky_clauses: string[];
};

export type Task = {
  id: string;
  title: string;
  description?: string | null;
  assignee: string;
  priority: "low" | "medium" | "high" | "urgent";
  due_date: string | null;
  status: "todo" | "in_progress" | "done";
  project?: string | null;
  tags?: string[];
  progress_percent?: number;
  ai_suggestions?: string | null;
  ai_reminder_enabled?: boolean;
};

export type TaskCreate = Pick<Task, "title" | "priority"> & Partial<Pick<Task, "description" | "due_date" | "project" | "tags" | "ai_reminder_enabled">> & { assigned_to?: string | null; estimated_hours?: number | null };

export type WorkflowAction = {
  type: string;
  name: string;
  config: Record<string, string | number | boolean>;
  order: number;
  retry_count?: number;
  delay_seconds?: number | null;
};

export type Workflow = {
  id: string;
  name: string;
  description?: string | null;
  status: "active" | "inactive" | "draft" | "archived";
  trigger: { type: string; conditions?: Record<string, unknown> | null };
  actions: WorkflowAction[];
  execution_count?: number;
  last_executed_at?: string | null;
};

export type WorkflowCreate = Omit<Workflow, "id" | "execution_count" | "last_executed_at">;

export type DashboardMetrics = {
  total_sales: number;
  revenue: number;
  expenses: number;
  customer_growth: number;
  new_leads: number;
};

export type ChartPoint = {
  date: string;
  value: number;
};

export type ForecastSeries = { points: ChartPoint[]; confidence: number; analysis: string; upside: number; downside: number; recommendations: string[] };
