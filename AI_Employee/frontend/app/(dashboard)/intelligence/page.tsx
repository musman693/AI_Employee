import type { Metadata } from "next";
import { IntelligenceModule } from "@/modules/intelligence";

export const metadata: Metadata = { title: "Intelligence | AI Employee OS", description: "Meeting transcription, document OCR and legal analysis." };
export default function IntelligencePage() { return <IntelligenceModule />; }
