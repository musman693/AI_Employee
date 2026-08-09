"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { authClient } from "@/lib/api/auth";
import Link from "next/link";

const schema = z.object({ email: z.string().email() });

type FormValues = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const { register, handleSubmit, formState } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const [message, setMessage] = useState("");

  async function onSubmit(data: FormValues) {
    setMessage("");
    try {
      const res = await authClient.requestPasswordReset(data.email);
      setMessage(res.message || "If an account exists, a reset email was sent.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Could not process request.");
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-semibold">Reset your password</h1>
        <p className="text-sm text-muted-foreground">Enter your account email and we'll send a reset link.</p>
      </div>
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
        <label className="grid gap-2 text-sm font-medium text-foreground">
          Email
          <Input type="email" placeholder="you@company.com" {...register("email")} />
        </label>
        <div className="flex items-center justify-between gap-3">
          <Link href="/auth/login" className="text-sm text-muted-foreground hover:text-foreground">Back to sign in</Link>
          <Button type="submit" disabled={formState.isSubmitting}>Send reset link</Button>
        </div>
      </form>
      {message && <div className="rounded-2xl border border-border bg-muted p-4 text-sm">{message}</div>}
    </div>
  );
}
