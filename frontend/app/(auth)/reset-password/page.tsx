"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { authClient } from "@/lib/api/auth";
import { useSearchParams, useRouter } from "next/navigation";

const schema = z.object({ password: z.string().min(8, "Password must be at least 8 characters") });

type FormValues = z.infer<typeof schema>;

export default function ResetPasswordPage() {
  const search = useSearchParams();
  const token = search.get("token") ?? "";
  const router = useRouter();
  const { register, handleSubmit, formState } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function onSubmit(data: FormValues) {
    setError("");
    try {
      await authClient.resetPassword(token, data.password);
      setMessage("Password reset successfully. Redirecting to sign in...");
      setTimeout(() => router.push("/auth/login"), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reset password.");
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-semibold">Create a new password</h1>
        <p className="text-sm text-muted-foreground">Enter a new password to continue.</p>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <label className="grid gap-2 text-sm font-medium text-foreground">
          New password
          <Input type="password" {...register("password")} />
        </label>
        <div className="flex items-center justify-end">
          <Button type="submit" disabled={formState.isSubmitting}>Set password</Button>
        </div>
      </form>
      {error && <div className="rounded-2xl border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive">{error}</div>}
      {message && <div className="rounded-2xl border border-primary/20 bg-primary/10 p-4 text-sm text-primary-foreground">{message}</div>}
    </div>
  );
}
