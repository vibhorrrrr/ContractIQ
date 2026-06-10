"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import { api, type DashboardStats } from "../../../lib/api";
import { riskBgColor, statusBadgeClass, statusLabel, formatDate } from "../../../lib/utils";
import Link from "next/link";

export default function DashboardPage() {
  const { getToken } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const token = await getToken();
        if (token) {
          const data = await api.getDashboardStats(token);
          setStats(data);
        }
      } catch (err) {
        console.error("Failed to load dashboard:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [getToken]);

  if (loading) {
    return (
      <div>
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="glass-card p-6">
              <div className="skeleton h-4 w-24 mb-3" />
              <div className="skeleton h-8 w-16" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const riskDistribution = stats?.risk_distribution || {};
  const totalRiskItems = Object.values(riskDistribution).reduce((a, b) => a + b, 0);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Link
          href="/contracts"
          className="px-5 py-2.5 text-sm font-medium rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition-all shadow-lg shadow-blue-500/25"
        >
          Upload Contract
        </Link>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div className="glass-card p-6 glow-blue">
          <p className="text-sm text-slate-400 mb-1">Total Contracts</p>
          <p className="text-3xl font-bold">{stats?.total_contracts ?? 0}</p>
        </div>
        <div className="glass-card p-6">
          <p className="text-sm text-slate-400 mb-1">Avg Risk Score</p>
          <p className="text-3xl font-bold">
            {stats?.avg_risk_score != null ? stats.avg_risk_score.toFixed(1) : "—"}
            <span className="text-sm text-slate-500 font-normal">/10</span>
          </p>
        </div>
        <div className="glass-card p-6">
          <p className="text-sm text-slate-400 mb-1">High/Critical Risks</p>
          <p className="text-3xl font-bold text-orange-400">
            {(riskDistribution["HIGH"] || 0) + (riskDistribution["CRITICAL"] || 0)}
          </p>
        </div>
        <div className="glass-card p-6 glow-emerald">
          <p className="text-sm text-slate-400 mb-1">Low Risk</p>
          <p className="text-3xl font-bold text-emerald-400">
            {riskDistribution["LOW"] || 0}
          </p>
        </div>
      </div>

      {/* Risk Distribution */}
      {totalRiskItems > 0 && (
        <div className="glass-card p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">Risk Distribution</h2>
          <div className="flex gap-2 h-4 rounded-full overflow-hidden bg-slate-800">
            {(["CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map((level) => {
              const count = riskDistribution[level] || 0;
              const pct = (count / totalRiskItems) * 100;
              if (pct === 0) return null;
              const colors: Record<string, string> = {
                CRITICAL: "bg-red-500",
                HIGH: "bg-orange-500",
                MEDIUM: "bg-yellow-500",
                LOW: "bg-emerald-500",
              };
              return (
                <div
                  key={level}
                  className={`${colors[level]} transition-all duration-500`}
                  style={{ width: `${pct}%` }}
                  title={`${level}: ${count}`}
                />
              );
            })}
          </div>
          <div className="flex gap-6 mt-3">
            {(["CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map((level) => (
              <div key={level} className="flex items-center gap-2 text-xs text-slate-400">
                <span
                  className={`w-2.5 h-2.5 rounded-full ${
                    { CRITICAL: "bg-red-500", HIGH: "bg-orange-500", MEDIUM: "bg-yellow-500", LOW: "bg-emerald-500" }[level]
                  }`}
                />
                {level}: {riskDistribution[level] || 0}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent uploads */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Uploads</h2>
        {stats?.recent_uploads.length === 0 ? (
          <p className="text-slate-500 text-sm">
            No contracts uploaded yet.{" "}
            <Link href="/contracts" className="text-blue-400 hover:underline">
              Upload your first contract
            </Link>
          </p>
        ) : (
          <div className="space-y-3">
            {stats?.recent_uploads.map((c) => (
              <Link
                key={c.id}
                href={`/contracts/${c.id}`}
                className="flex items-center justify-between p-4 rounded-xl bg-slate-800/30 hover:bg-slate-800/60 border border-slate-700/30 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-slate-700/50 flex items-center justify-center text-sm">
                    📄
                  </div>
                  <div>
                    <p className="text-sm font-medium group-hover:text-blue-400 transition-colors">
                      {c.filename}
                    </p>
                    <p className="text-xs text-slate-500">{formatDate(c.upload_date)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {c.risk_level && (
                    <span
                      className={`px-2.5 py-1 text-xs font-medium rounded-lg border ${riskBgColor(c.risk_level)}`}
                    >
                      {c.risk_level}
                    </span>
                  )}
                  <span
                    className={`px-2.5 py-1 text-xs font-medium rounded-lg border ${statusBadgeClass(c.status)}`}
                  >
                    {statusLabel(c.status)}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
