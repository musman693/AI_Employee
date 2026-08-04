export type MeetingAnalysis = {
  summary: string;
  action_items: Array<string | { task?: string; assignee?: string }>;
  speakers: string[];
  deadlines: string[];
  raw_transcript: string;
  file_url: string;
};

export type MeetingResponse = { status: string; data: MeetingAnalysis };
export type DocumentUpload = { document_id: string; s3_url: string; indexing_status: string; extracted_snippet: string };
export type SearchResult = { document_id: string; filename: string; content: string };
export type SearchResponse = { query: string; results: SearchResult[] };
export type ContractAnalysis = { risk_level: "High" | "Medium" | "Low"; risky_clauses: string[]; summary: string };
export type ContractResponse = { status: string; analysis: ContractAnalysis };
