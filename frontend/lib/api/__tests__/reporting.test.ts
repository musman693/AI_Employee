import { beforeEach, describe, expect, it, vi } from "vitest";

const { get } = vi.hoisted(() => ({ get: vi.fn() }));
vi.mock("@/lib/api/base", () => ({ apiClient: { get } }));

import { reportingApi } from "../reporting";

describe("reportingApi", () => {
  beforeEach(() => get.mockReset());

  it("combines dashboard endpoints into normalized metrics", async () => {
    get.mockResolvedValueOnce({ data: { total_sales: 1200 } }).mockResolvedValueOnce({ data: { total_revenue: 1000 } }).mockResolvedValueOnce({ data: { total_expenses: 400 } }).mockResolvedValueOnce({ data: { new_customers: 5, total_customers: 20 } });
    await expect(reportingApi.getDashboard("90d")).resolves.toEqual({ total_sales: 1200, revenue: 1000, expenses: 400, customer_growth: 25, new_leads: 5 });
    expect(get).toHaveBeenCalledWith(expect.stringContaining("period=current_quarter"));
  });

  it("normalizes forecast scenarios and range", async () => {
    get.mockResolvedValue({ data: { forecast_months: [{ month: "September", forecast: 1500 }], confidence_percent: 82, ai_analysis: "Healthy growth", upside_scenario: 1800, downside_scenario: 1200, recommendations: ["Accelerate pipeline"] } });
    await expect(reportingApi.getForecastSeries("90d")).resolves.toEqual({ points: [{ date: "September", value: 1500 }], confidence: 82, analysis: "Healthy growth", upside: 1800, downside: 1200, recommendations: ["Accelerate pipeline"] });
    expect(get).toHaveBeenCalledWith(expect.stringContaining("period=next_quarter"));
  });
});
