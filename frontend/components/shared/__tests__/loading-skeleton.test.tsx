import { render } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { LoadingSkeleton } from "../loading-skeleton";

describe("LoadingSkeleton", () => {
  it("renders the given number of rows", () => {
    const { container } = render(<LoadingSkeleton rows={3} />);
    const items = container.querySelectorAll(".h-16");
    expect(items.length).toBe(3);
  });
});
