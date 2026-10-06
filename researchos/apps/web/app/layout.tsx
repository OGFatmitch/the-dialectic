import type { Metadata } from "next";
import "./styles.css";
import "./costs.css";

export const metadata: Metadata = { title: "ResearchOS", description: "High-integrity autonomous research" };

export default function Layout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
