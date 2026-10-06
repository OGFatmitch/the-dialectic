"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import type { Project, ResearchPlan, Source } from "@researchos/shared-types";
import { api } from "@/lib/api";

export default function Workspace({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params); const [project, setProject] = useState<Project>(); const [plan, setPlan] = useState<ResearchPlan | null>(null); const [sources, setSources] = useState<Source[]>([]); const [busy, setBusy] = useState(""); const [message, setMessage] = useState("");
  async function refresh() { const [p, pl, so] = await Promise.all([api.project(id), api.plan(id), api.sources(id)]); setProject(p); setPlan(pl); setSources(so); }
  useEffect(() => { refresh().catch(err => setMessage(err.message)); }, [id]);
  async function act(name: string, operation: () => Promise<unknown>) { setBusy(name); setMessage(""); try { await operation(); await refresh(); } catch (err) { setMessage(err instanceof Error ? err.message : "Action failed"); } finally { setBusy(""); } }
  if (!project) return <main className="shell"><p className="loading">Loading research state…</p></main>;
  return <main className="shell"><header className="masthead"><Link className="brand" href="/"><span className="mark">R</span><span>ResearchOS</span></Link><span className="tag">{project.venue}</span></header>
    <div className="workspace-head"><div><p className="eyebrow">{project.stage.replaceAll("_", " ")}</p><h1>{project.title}</h1><p className="lede">{project.research_question}</p></div><div className="actions">{project.stage === "IDEA" && <button onClick={() => act("approve", () => api.approveBrief(id))} disabled={!!busy}>Approve brief</button>}<button className="secondary" onClick={() => act("plan", () => api.generatePlan(id))} disabled={!!busy}>{plan ? "Regenerate plan" : "Generate plan"}</button><button onClick={() => act("search", () => api.search(id))} disabled={!!busy}>{busy === "search" ? "Searching…" : "Run literature search"}</button></div></div>
    {message && <p className="error">{message}</p>}
    <nav className="tabs"><span>Brief</span><b>Research</b><span>Sources <i>{sources.length}</i></span><span>Evidence</span><span>Thesis</span><span>Draft</span><span>Reviews</span></nav>
    <div className="workspace-grid"><section className="panel"><div className="panel-title"><div><p className="eyebrow">Research Director</p><h2>Research plan</h2></div>{plan && <span>v{plan.version}</span>}</div>{plan ? <article className="plan">{plan.content.split("\n").map((line, index) => line.startsWith("#") ? <h3 key={index}>{line.replace(/^#+ /, "")}</h3> : line.startsWith("- ") ? <p className="bullet" key={index}>→ {line.slice(2)}</p> : <p key={index}>{line}</p>)}</article> : <div className="empty small">Generate a plan before formal research begins.</div>}</section>
    <section className="panel"><div className="panel-title"><div><p className="eyebrow">Evidence Librarian</p><h2>Candidate sources</h2></div><span>{sources.length} found</span></div><div className="sources">{sources.map(source => <article className="source" key={source.id}><div className="source-top"><span className="source-type">{source.source_type}</span><span>{Math.round(source.relevance_score * 100)}% relevance</span></div><h3>{source.title}</h3><p>{source.authors.join(", ")} · {source.publication_year}</p><p className="reason">{source.relevance_reason}</p><footer><span className="candidate">{source.status}</span>{source.url && <a href={source.url} target="_blank">Inspect source ↗</a>}</footer></article>)}{!sources.length && <div className="empty small">No candidate sources. Run the decomposed literature search.</div>}</div></section></div>
  </main>;
}
