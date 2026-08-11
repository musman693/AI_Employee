"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { authClient } from "@/lib/api/auth";
import { ArrowRight } from "lucide-react";

const signupSchema = z.object({
  name: z.string().min(3, "Enter your full name"),
  email: z.string().email({ message: "Enter a valid email" }),
  password: z.string().min(8, "Password must have at least 8 characters"),
});

type SignupFormValues = z.infer<typeof signupSchema>;

export default function SignupPage() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormValues>({ resolver: zodResolver(signupSchema) });

  async function onSubmit(data: SignupFormValues) {
    setErrorMessage("");
    setSuccessMessage("");
    try {
      await authClient.signup({ name: data.name, email: data.email, password: data.password });
      setSuccessMessage("Account created successfully. Check your email for the next step.");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to create an account.";
      setErrorMessage(message);
    }
  }

  return (
    <div className="space-y-8">
      <div className="space-y-3 text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.35em] text-muted-foreground">Create your workspace</p>
        <h1 className="text-3xl font-semibold text-foreground">Sign up for AI Employee OS</h1>
        <p className="mx-auto max-w-xl text-sm leading-6 text-muted-foreground">
          Start by creating your account and connecting your business systems in one secure platform.
        </p>
      </div>
      <form noValidate className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
        <div className="grid gap-4">
          <label className="grid gap-2 text-sm font-medium text-foreground">
            Full name
            <Input placeholder="Your full name" {...register("name")} />
            {errors.name && <span className="text-xs text-destructive">{errors.name.message}</span>}
          </label>
          <label className="grid gap-2 text-sm font-medium text-foreground">
            Business email
            <Input type="email" placeholder="you@company.com" {...register("email")} />
            {errors.email && <span className="text-xs text-destructive">{errors.email.message}</span>}
          </label>
          <label className="grid gap-2 text-sm font-medium text-foreground">
            Create a password
            <Input type="password" placeholder="••••••••" {...register("password")} />
            {errors.password && <span className="text-xs text-destructive">{errors.password.message}</span>}
          </label>
        </div>
        {errorMessage && <div className="rounded-2xl border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive">{errorMessage}</div>}
        {successMessage && <div className="rounded-2xl border border-primary/20 bg-primary/10 p-4 text-sm text-primary-foreground">{successMessage}</div>}
        <div className="flex items-center justify-between gap-3">
          <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground">
            Already have an account?
          </Link>
          <Button type="submit" className="inline-flex items-center gap-2" disabled={isSubmitting}>
            Create account
            <ArrowRight size={16} />
          </Button>
        </div>
      </form>
    </div>
  );
}
