import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import Link from "next/link";

export default async function HomePage() {
  const { userId } = await auth();
  if (userId) redirect("/dashboard");

  return (
    <div className="gradient-bg min-h-screen flex flex-col">
      {/* Nav */}
      <nav className="glass sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm">
            CQ
          </div>
          <span className="text-xl font-semibold tracking-tight">ContractIQ</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/sign-in"
            className="px-4 py-2 text-sm text-slate-300 hover:text-white transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/sign-up"
            className="px-5 py-2.5 text-sm font-medium rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 text-center max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm mb-8">
          <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
          AI-Powered Contract Intelligence
        </div>

        <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight mb-6">
          Turn contracts into{" "}
          <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            actionable intelligence
          </span>
        </h1>

        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10 leading-relaxed">
          Upload any contract. Get instant risk analysis, clause extraction, and executive
          summaries powered by AI. Every finding traced to source text.
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link
            href="/sign-up"
            className="px-8 py-3.5 text-base font-medium rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-0.5"
          >
            Start Analyzing →
          </Link>
          <Link
            href="/sign-in"
            className="px-8 py-3.5 text-base font-medium rounded-xl glass text-slate-300 hover:text-white transition-all hover:-translate-y-0.5"
          >
            Sign In
          </Link>
        </div>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-3 mt-16">
          {[
            "Risk Scoring",
            "Clause Extraction",
            "Executive Summaries",
            "Negotiation Points",
            "Source Tracing",
          ].map((feature) => (
            <div
              key={feature}
              className="px-4 py-2 rounded-full bg-slate-800/50 border border-slate-700/50 text-sm text-slate-400"
            >
              {feature}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
