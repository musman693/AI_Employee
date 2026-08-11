"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { signIn } from "next-auth/react";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import Link from "next/link";
import { Mail, Lock, ArrowRight } from "lucide-react";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "Password must have at least 8 characters"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [errorMessage, setErrorMessage] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(data: LoginFormValues) {
    setErrorMessage("");
    const result = await signIn("credentials", {
      redirect: false,
      email: data.email,
      password: data.password,
    });

    if (result?.error) {
      setErrorMessage(result.error);
      return;
    }

    router.push("/inbox");
  }

  return (
    <div className="space-y-8">
      <div className="space-y-3 text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.35em] text-muted-foreground">Welcome back</p>
        <h1 className="text-3xl font-semibold text-foreground">Sign in to AI Employee OS</h1>
        <p className="mx-auto max-w-xl text-sm leading-6 text-muted-foreground">
          Access your inbox, pipeline, documents, tasks, and business reports from one intelligent workspace.
        </p>
      </div>
      <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
        <div className="grid gap-4">
          <label className="grid gap-2 text-sm font-medium text-foreground">
            Email
            <Input type="email" autoComplete="email" placeholder="you@company.com" {...register("email")} />
            {errors.email && <span className="text-xs text-destructive">{errors.email.message}</span>}
          </label>
          <label className="grid gap-2 text-sm font-medium text-foreground">
            Password
            <Input type="password" autoComplete="current-password" placeholder="••••••••" {...register("password")} />
            {errors.password && <span className="text-xs text-destructive">{errors.password.message}</span>}
          </label>
        </div>
        {errorMessage && <div className="rounded-2xl border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive">{errorMessage}</div>}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <Link href="/forgot-password" className="text-sm text-primary hover:text-primary-foreground">
            Forgot password?
          </Link>
          <Button type="submit" className="inline-flex items-center gap-2" disabled={isSubmitting}>
            Continue
            <ArrowRight size={16} />
          </Button>
        </div>
      </form>
      <div className="rounded-3xl border border-border bg-muted p-4 text-sm text-muted-foreground">
        New to AI Employee OS? <Link href="/signup" className="font-semibold text-foreground hover:text-primary">Create an account</Link>.
      </div>
    </div>
  );
}
