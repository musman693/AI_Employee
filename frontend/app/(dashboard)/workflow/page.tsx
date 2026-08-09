import type { Metadata } from "next";
import { WorkflowModule } from "@/modules/workflow/workflow-module";

export const metadata: Metadata = { title: "Workflows | AI Employee OS", description: "Create automation workflows" };

export default function WorkflowPage() {
  return <main style={{ padding: 24 }}><WorkflowModule /></main>;
}
