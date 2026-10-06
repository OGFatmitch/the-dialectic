"use client";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { Project } from "@researchos/shared-types";
import { api } from "@/lib/api";

const seed = {
  title: "Governing Autonomous AI at Scale: An Enterprise Control Plane for Agentic Systems",
  research_question: "What architectural controls are required to safely increase autonomy in enterprise AI systems?",
  initial_thesis: "Enterprises need an autonomy control plane distinct from conventional application infrastructure.",
  venue: "IEEE Software", target_submission_date: "2026-11-05",
};

export default function Dashboard() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { api.projects().then(setProjects).catch(() => setError("Start the API to load projects.")); }, []);
  async function create(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try { const project = await api.createProject(seed); router.push(`/projects/${project.id}`); }
    catch (err) { setError(err instanceof Error ? err.message : "Could not create project"); setBusy(false); }
  }
  return <main className="shell">
    <header className="masthead"><div className="brand"><span className="mark">R</span><span>ResearchOS</span></div><span className="tag">Evidence before prose</span></header>
    <section className="hero"><div><p className="eyebrow">Research command center</p><h1>Make every claim<br/><em>answerable.</em></h1><p className="lede">A rigorous workspace for evidence, argument, adversarial review, and publication—with provenance at every step.</p></div><div className="quality-card"><p>RESEARCH QUALITY</p><div className="quality-row"><span>Source integrity</span><b>Traceable</b></div><div className="quality-row"><span>Contradiction search</span><b>Required</b></div><div className="quality-row"><span>Human gates</span><b>5 active</b></div></div></section>
    <section className="section-head"><div><p className="eyebrow">Active work</p><h2>Projects</h2></div><form onSubmit={create}><button disabled={busy}>{busy ? "Creating…" : "+ Start seeded project"}</button></form></section>
    {error && <p className="error">{error}</p>}
    <div className="project-grid">{projects.map(project => <button className="project-card" key={project.id} onClick={() => router.push(`/projects/${project.id}`)}><div className="stage">{project.stage.replaceAll("_", " ")}</div><h3>{project.title}</h3><p>{project.research_question}</p><footer><span>{project.venue}</span><span>Open →</span></footer></button>)}{!projects.length && !error && <div className="empty">No projects yet. Begin with the seeded IEEE Software study.</div>}</div>
  </main>;
}
