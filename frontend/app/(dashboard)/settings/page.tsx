import type { Metadata } from "next";
import { Topbar } from "@/components/shared/topbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export const metadata: Metadata = {
  title: "Settings | AI Employee OS",
  description: "Manage your profile, company settings, permissions, and integrations.",
};

export default function SettingsPage() {
  return (
    <div className="flex-1 overflow-auto p-6 lg:p-8">
      <Topbar title="Settings" subtitle="Account and integrations" />
      <section className="mt-8 grid gap-8 lg:grid-cols-[minmax(0,1.35fr)_minmax(0,0.65fr)]">
        <div className="space-y-8">
          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-foreground">Profile</h2>
            <p className="mt-2 text-sm text-muted-foreground">Update your personal and company details.</p>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <label className="grid gap-2 text-sm font-medium text-foreground">
                Full name
                <Input placeholder="Nouman Khan" />
              </label>
              <label className="grid gap-2 text-sm font-medium text-foreground">
                Email address
                <Input type="email" placeholder="nouman@acmestudio.com" />
              </label>
              <label className="grid gap-2 text-sm font-medium text-foreground sm:col-span-2">
                Company name
                <Input placeholder="Acme Studio" />
              </label>
              <label className="grid gap-2 text-sm font-medium text-foreground sm:col-span-2">
                Role / permission
                <Input placeholder="Administrator" />
              </label>
            </div>
          </div>
          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-foreground">Integrations</h2>
                <p className="mt-2 text-sm text-muted-foreground">Connect Gmail, Outlook, and WhatsApp.
                </p>
              </div>
              <Button variant="outline">Manage marketplace</Button>
            </div>
            <div className="mt-6 space-y-4">
              {[
                { name: "Gmail", status: "Connected" },
                { name: "Outlook", status: "Connected" },
                { name: "WhatsApp", status: "Disconnected" },
              ].map((integration) => (
                <div key={integration.name} className="flex flex-wrap items-center justify-between gap-3 rounded-3xl border border-border bg-muted p-4">
                  <div>
                    <p className="font-semibold text-foreground">{integration.name}</p>
                    <p className="text-sm text-muted-foreground">{integration.status}</p>
                  </div>
                  <Button variant={integration.status === "Connected" ? "outline" : "default"} size="sm">
                    {integration.status === "Connected" ? "Disconnect" : "Connect"}
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </div>
        <aside className="space-y-6">
          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-foreground">Security</h2>
            <p className="mt-2 text-sm text-muted-foreground">Enable MFA and manage account recovery settings.</p>
            <div className="mt-6 space-y-4">
              <div className="rounded-3xl border border-border bg-muted p-4">
                <p className="text-sm font-semibold text-foreground">Multi-factor authentication</p>
                <p className="mt-1 text-sm text-muted-foreground">One-time passwords for every login.</p>
                <Button variant="ghost" className="mt-4 w-full">Configure MFA</Button>
              </div>
              <div className="rounded-3xl border border-border bg-muted p-4">
                <p className="text-sm font-semibold text-foreground">Permissions</p>
                <p className="mt-1 text-sm text-muted-foreground">Invite teammates and manage roles.</p>
                <Button variant="ghost" className="mt-4 w-full">Invite team</Button>
              </div>
            </div>
          </div>
          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-foreground">Support</h2>
            <p className="mt-2 text-sm text-muted-foreground">Need help? Reach out to our success team.</p>
            <Button variant="outline" className="mt-5 w-full">Contact support</Button>
          </div>
        </aside>
      </section>
    </div>
  );
}
