import type { ContractResponse, DocumentUpload, MeetingResponse, SearchResponse } from "./intelligence-types";

const API = "/api/backend/api/v1";

async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "The request could not be completed." }));
    throw new Error(payload.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

function upload(path: string, file: File) {
  const body = new FormData(); body.append("file", file);
  return fetch(`${API}${path}`, { method: "POST", body });
}

export const intelligenceApi = {
  processMeeting: (file: File) => upload("/meeting/process-meeting", file).then((response) => parse<MeetingResponse>(response)),
  uploadDocument: (file: File) => upload("/document/upload-ocr", file).then((response) => parse<DocumentUpload>(response)),
  searchDocuments: (query: string) => fetch(`${API}/document/search?q=${encodeURIComponent(query)}`, { cache: "no-store" }).then((response) => parse<SearchResponse>(response)),
  analyzeContract: (contractText: string) => fetch(`${API}/legal/analyze-contract`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ contract_text: contractText }) }).then((response) => parse<ContractResponse>(response)),
};
