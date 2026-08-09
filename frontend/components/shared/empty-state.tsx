import { Sparkles } from "lucide-react";

export function EmptyState({ title, description, action }: { title: string; description: string; action: React.ReactNode }) {
  return (
    <div className="rounded-3xl border border-border bg-muted p-10 text-center text-muted-foreground">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-primary/10 text-primary">
        <Sparkles size={24} />
      </div>
      <h2 className="mt-6 text-lg font-semibold text-foreground">{title}</h2>
      <p className="mt-3 text-sm leading-6">{description}</p>
      <div className="mt-6">{action}</div>
    </div>
  );
}
