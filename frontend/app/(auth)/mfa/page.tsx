"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { authClient } from "@/lib/api/auth";
import { useRouter } from "next/navigation";

const schema = z.object({ otp: z.string().min(4).max(8) });

type FormValues = z.infer<typeof schema>;

export default function MfaPage() {
  const { register, handleSubmit, formState } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const [error, setError] = useState("");
  const router = useRouter();

  async function onSubmit(data: FormValues) {
    setError("");
    try {
      const res = await authClient.verifyOtp(data.otp);
      if (res.verified) {
        router.push("/dashboard/inbox");
      } else {
        setError("OTP verification failed. Please try again.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed.");
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-semibold">Enter one-time code</h1>
        <p className="text-sm text-muted-foreground">Enter the code sent to your authenticator or email.</p>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <label className="grid gap-2 text-sm font-medium text-foreground">
          One-time code
          <Input type="text" placeholder="123456" {...register("otp")} />
        </label>
        <div className="flex items-center justify-end">
          <Button type="submit" disabled={formState.isSubmitting}>Verify</Button>
        </div>
      </form>
      {error && <div className="rounded-2xl border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive">{error}</div>}
    </div>
  );
}
