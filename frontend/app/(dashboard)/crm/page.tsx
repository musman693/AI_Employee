import type { Metadata } from "next";
import { CrmModule } from "@/modules/crm";

export const metadata: Metadata = {
  title: "CRM & Pipeline | AI Employee OS",
  description: "Manage customers, leads, deals, and relationship insights.",
};

export default function CrmPage() {
  return <CrmModule />;
}
