export type Stage = "New lead" | "Qualified" | "Proposal" | "Negotiation" | "Won";

export type Lead = {
  id: number;
  name: string;
  company: string;
  initials: string;
  role: string;
  email: string;
  phone: string;
  value: number;
  stage: Stage;
  probability: number;
  lastActivity: string;
  nextStep: string;
  source: string;
  color: string;
  insight: string;
};

export const stages: Stage[] = ["New lead", "Qualified", "Proposal", "Negotiation", "Won"];

export const initialLeads: Lead[] = [
  { id: 1, name: "Sarah Mitchell", company: "Northstar Studio", initials: "SM", role: "Marketing Director", email: "sarah@northstar.studio", phone: "+1 415 555 0182", value: 28500, stage: "Proposal", probability: 68, lastActivity: "Email replied 18m ago", nextStep: "Review campaign timeline", source: "Referral", color: "#d76748", insight: "Highly engaged and actively involving leadership. A clear delivery timeline is the strongest path to close." },
  { id: 2, name: "Omar Farooq", company: "Crescent Retail", initials: "OF", role: "Operations Manager", email: "omar@crescentretail.com", phone: "+92 300 555 0142", value: 42000, stage: "Negotiation", probability: 82, lastActivity: "WhatsApp message 42m ago", nextStep: "Send revised payment terms", source: "Website", color: "#347c6a", insight: "Commercial intent is strong. The only remaining concern is a staged payment schedule." },
  { id: 3, name: "Elena Rossi", company: "Forma Labs", initials: "ER", role: "Co-founder", email: "elena@formalabs.co", phone: "+39 02 555 0188", value: 18000, stage: "Qualified", probability: 46, lastActivity: "Meeting booked yesterday", nextStep: "Discovery call on Thursday", source: "LinkedIn", color: "#6c71b5", insight: "Good product fit, but buying authority and implementation timing still need to be confirmed." },
  { id: 4, name: "David Chen", company: "Arcline Systems", initials: "DC", role: "Procurement Lead", email: "david@arcline.io", phone: "+1 604 555 0124", value: 64000, stage: "New lead", probability: 24, lastActivity: "Form submitted yesterday", nextStep: "Confirm inventory requirements", source: "Website", color: "#b06f3e", insight: "Large opportunity with an urgent delivery window. Responding today will materially improve conversion odds." },
  { id: 5, name: "Maya Thompson", company: "Fieldwork Co.", initials: "MT", role: "Brand Manager", email: "maya@fieldwork.co", phone: "+44 20 5550 0171", value: 21500, stage: "Won", probability: 100, lastActivity: "Contract signed Mon", nextStep: "Schedule kickoff", source: "Referral", color: "#48769a", insight: "Closed successfully. A smooth kickoff creates an immediate expansion opportunity for content production." },
  { id: 6, name: "Adeel Hussain", company: "Vertex Textiles", initials: "AH", role: "Commercial Director", email: "adeel@vertextextiles.pk", phone: "+92 321 555 0199", value: 35500, stage: "Qualified", probability: 51, lastActivity: "Call completed 2d ago", nextStep: "Share implementation plan", source: "Event", color: "#7a654b", insight: "The team has budget approval. Technical onboarding confidence is the main decision factor." },
  { id: 7, name: "Lucy Park", company: "Kindred Health", initials: "LP", role: "Practice Manager", email: "lucy@kindred.health", phone: "+1 212 555 0166", value: 12750, stage: "Proposal", probability: 64, lastActivity: "Proposal opened 3h ago", nextStep: "Follow up Friday", source: "Partner", color: "#916276", insight: "Proposal engagement is positive. Follow up with a concise compliance and data-security summary." },
];

export const activities = [
  { title: "Replied to Q3 campaign proposal", detail: "Email · Sarah Mitchell", time: "18 min ago", tone: "green" },
  { title: "Moved to Negotiation", detail: "Crescent Retail · PKR 11.7M", time: "42 min ago", tone: "amber" },
  { title: "Discovery call scheduled", detail: "Forma Labs · Thursday, 2:00 PM", time: "Yesterday", tone: "blue" },
  { title: "New website lead captured", detail: "Arcline Systems · 40-unit enquiry", time: "Yesterday", tone: "violet" },
];
