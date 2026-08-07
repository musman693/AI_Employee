import type { Metadata } from "next";
import { FinanceModule } from "@/modules/finance";

export const metadata: Metadata = { title: "Finance | AI Employee OS", description: "Quotations, invoices, payments, and AI finance insights." };
export default function FinancePage() { return <FinanceModule />; }
