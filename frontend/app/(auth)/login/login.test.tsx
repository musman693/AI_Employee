import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));
vi.mock("next-auth/react", () => ({ signIn: vi.fn() }));

import LoginPage from "./page";

describe("LoginPage", () => {
  it("shows application validation errors for invalid credentials", async () => {
    const user = userEvent.setup();
    render(<LoginPage />);
    await user.type(screen.getByLabelText("Email"), "not-an-email");
    await user.type(screen.getByLabelText("Password"), "short");
    await user.click(screen.getByRole("button", { name: "Continue" }));
    expect(screen.queryByText("Enter a valid email")).not.toBeNull();
    expect(screen.queryByText("Password must have at least 8 characters")).not.toBeNull();
  });
});
