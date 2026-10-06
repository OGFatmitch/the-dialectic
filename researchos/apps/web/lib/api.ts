import type { AgentRun, Project, ResearchPlan, SearchRun, Source } from "@researchos/shared-types";
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers }, cache: "no-store" });
  if (!response.ok) throw new Error((await response.json()).detail ?? "Request failed");
  return response.json();
}
export const api = {
  projects: () => request<Project[]>("/projects"),
  project: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (data: object) => request<Project>("/projects", { method: "POST", body: JSON.stringify(data) }),
  approveBrief: (id: string) => request<Project>(`/projects/${id}/transition`, { method: "POST", body: JSON.stringify({ target: "BRIEF_APPROVED", reason: "Human approved research brief" }) }),
  plan: (id: string) => request<ResearchPlan | null>(`/projects/${id}/research-plan`),
  generatePlan: (id: string) => request<ResearchPlan>(`/projects/${id}/research-plan`, { method: "POST" }),
  search: (id: string) => request<SearchRun>(`/projects/${id}/search`, { method: "POST", body: JSON.stringify({ provider: "openai" }) }),
  sources: (id: string) => request<Source[]>(`/projects/${id}/sources`),
  reviewSources: (id: string, sourceIds: string[], decision: "accepted" | "rejected") => request<{ updated: number }>(`/projects/${id}/sources/review`, { method: "POST", body: JSON.stringify({ source_ids: sourceIds, decision }) }),
  runs: (id: string) => request<AgentRun[]>(`/projects/${id}/runs`),
};
