import type { Metadata } from "next";
import { SettingsModule } from "@/modules/settings/settings-module";

export const metadata: Metadata = {
  title: "Settings | AI Employee OS",
  description: "Manage your profile, security, team, and integrations.",
};

export default function SettingsPage() {
  return <SettingsModule />;
}
