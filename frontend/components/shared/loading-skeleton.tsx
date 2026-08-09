export function LoadingSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="h-16 rounded-3xl bg-muted/70 animate-pulse" />
      ))}
    </div>
  );
}
