"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState, use } from "react";
import Link from "next/link";
import { api, type ContractDetail, type RiskResponse } from "../../../../lib/api";
import {
  riskBgColor,
  statusBadgeClass,
  statusLabel,
  formatDate,
  formatFileSize,
} from "../../../../lib/utils";

export default function ContractDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { getToken } = useAuth();
  const [contract, setContract] = useState<ContractDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedRisk, setSelectedRisk] = useState<RiskResponse | null>(null);

  useEffect(() => {
    let pollInterval: NodeJS.Timeout;

    async function load() {
      try {
        const token = await getToken();
        if (!token) return;

        const data = await api.getContract(id, token);
        setContract(data);

        // Poll if still processing
        if (data.status === "pending" || data.status === "processing") {
          pollInterval = setInterval(async () => {
            const updated = await api.getContract(id, token);
            setContract(updated);
            if (updated.status === "completed" || updated.status === "failed") {
              clearInterval(pollInterval);
            }
          }, 3000);
        }
      } catch (err) {
        console.error("Failed to load contract:", err);
      } finally {
        setLoading(false);
      }
    }
    load();

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [id, getToken]);

  if (loading) {
    return (
      <div>
        <div className="skeleton h-8 w-64 mb-4" />
        <div className="skeleton h-4 w-96 mb-8" />
        <div className="glass-card p-6">
          <div className="skeleton h-6 w-48 mb-4" />
          <div className="skeleton h-24 w-full" />
        </div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="glass-card p-12 text-center">
        <p className="text-xl mb-2">🔍</p>
        <p className="text-slate-400">Contract not found.</p>
        <Link href="/contracts" className="text-blue-400 hover:underline text-sm mt-2 inline-block">
          ← Back to contracts
        </Link>
      </div>
    );
  }

  // Group clauses by type
  const clausesByType: Record<string, typeof contract.clauses> = {};
  for (const clause of contract.clauses) {
    if (!clausesByType[clause.clause_type]) {
      clausesByType[clause.clause_type] = [];
    }
    clausesByType[clause.clause_type].push(clause);
  }

  const isProcessing = contract.status === "pending" || contract.status === "processing";

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <Link
            href="/contracts"
            className="text-sm text-slate-500 hover:text-slate-300 transition-colors mb-2 inline-block"
          >
            ← Back to contracts
          </Link>
          <h1 className="text-2xl font-bold">{contract.filename}</h1>
          <div className="flex items-center gap-4 mt-2">
            <span
              className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-lg border ${statusBadgeClass(contract.status)}`}
            >
              {statusLabel(contract.status)}
            </span>
            <span className="text-sm text-slate-500">
              Uploaded {formatDate(contract.upload_date)}
            </span>
            {contract.page_count && (
              <span className="text-sm text-slate-500">
                {contract.page_count} pages
              </span>
            )}
            {contract.file_size && (
              <span className="text-sm text-slate-500">
                {formatFileSize(contract.file_size)}
              </span>
            )}
          </div>
        </div>

        {/* Risk score badge */}
        {contract.risk_score != null && (
          <div className="glass-card p-4 text-center min-w-[120px]">
            <p className="text-xs text-slate-400 mb-1">Risk Score</p>
            <p className={`text-3xl font-bold ${
              contract.risk_score > 7.5 ? "text-red-400" :
              contract.risk_score > 5 ? "text-orange-400" :
              contract.risk_score > 3 ? "text-yellow-400" : "text-emerald-400"
            }`}>
              {contract.risk_score.toFixed(1)}
            </p>
            <p className="text-xs text-slate-500">/10.0</p>
          </div>
        )}
      </div>

      {/* Processing state */}
      {isProcessing && (
        <div className="glass-card p-6 mb-6 flex items-center gap-4">
          <div className="w-10 h-10 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
          <div>
            <p className="font-medium text-blue-400">Analysing contract...</p>
            <p className="text-sm text-slate-400">
              This may take a minute. The page will update automatically.
            </p>
          </div>
        </div>
      )}

      {/* Error state */}
      {contract.status === "failed" && (
        <div className="glass-card p-6 mb-6 border-red-500/30">
          <p className="font-medium text-red-400 mb-1">Analysis Failed</p>
          <p className="text-sm text-slate-400">{contract.error_message}</p>
        </div>
      )}

      {/* Executive Summary */}
      {contract.summary && (
        <div className="glass-card p-6 mb-6 glow-blue">
          <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
            📋 Executive Summary
          </h2>
          <p className="text-slate-300 leading-relaxed">{contract.summary}</p>
        </div>
      )}

      {/* Content grid */}
      {contract.status === "completed" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Clauses */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-lg font-semibold">Extracted Clauses</h2>
            {Object.entries(clausesByType).map(([type, clauses]) => (
              <div key={type} className="glass-card p-5">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3">
                  {type.replace(/_/g, " ")}
                </h3>
                <div className="space-y-3">
                  {clauses.map((clause) => {
                    const relatedRisks = contract.risks.filter(
                      (r) => r.clause_id === clause.id
                    );
                    return (
                      <div
                        key={clause.id}
                        className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30"
                      >
                        <div className="flex items-center gap-2 mb-2">
                          {clause.risk_level && (
                            <span
                              className={`px-2 py-0.5 text-xs font-medium rounded-md border ${riskBgColor(clause.risk_level)}`}
                            >
                              {clause.risk_level}
                            </span>
                          )}
                          {clause.page_number && (
                            <span className="text-xs text-slate-500">
                              Page {clause.page_number}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-slate-300 leading-relaxed line-clamp-3">
                          {clause.clause_text}
                        </p>
                        {relatedRisks.map((risk) => (
                          <button
                            key={risk.id}
                            onClick={() => setSelectedRisk(risk)}
                            className="mt-2 text-xs text-blue-400 hover:text-blue-300 hover:underline transition-colors"
                          >
                            View finding: {risk.finding}
                          </button>
                        ))}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}

            {Object.keys(clausesByType).length === 0 && (
              <div className="glass-card p-8 text-center">
                <p className="text-slate-500">No clauses extracted.</p>
              </div>
            )}
          </div>

          {/* Risk detail panel */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Risk Details</h2>
            {selectedRisk ? (
              <div className="glass-card p-5 sticky top-8">
                <div className="flex items-center justify-between mb-4">
                  <span
                    className={`px-2.5 py-1 text-xs font-medium rounded-lg border ${riskBgColor(selectedRisk.severity)}`}
                  >
                    {selectedRisk.severity}
                  </span>
                  <button
                    onClick={() => setSelectedRisk(null)}
                    className="text-slate-500 hover:text-slate-300 text-sm"
                  >
                    ✕
                  </button>
                </div>
                <h3 className="font-semibold mb-2">{selectedRisk.finding}</h3>
                <div className="space-y-4 text-sm">
                  <div>
                    <p className="text-xs uppercase tracking-wider text-slate-500 mb-1">
                      Explanation
                    </p>
                    <p className="text-slate-300 leading-relaxed">
                      {selectedRisk.explanation}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wider text-slate-500 mb-1">
                      Recommendation
                    </p>
                    <p className="text-blue-300 leading-relaxed">
                      {selectedRisk.recommendation}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wider text-slate-500 mb-1">
                      Source Text
                    </p>
                    <blockquote className="p-3 rounded-lg bg-slate-800/50 border-l-2 border-blue-500/50 text-slate-400 text-xs leading-relaxed italic">
                      {selectedRisk.source_text}
                    </blockquote>
                  </div>
                  {selectedRisk.confidence != null && (
                    <div className="flex items-center gap-2">
                      <p className="text-xs text-slate-500">Confidence:</p>
                      <div className="flex-1 h-1.5 rounded-full bg-slate-800">
                        <div
                          className="h-full rounded-full bg-blue-500 transition-all"
                          style={{ width: `${selectedRisk.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-400 font-mono">
                        {(selectedRisk.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="glass-card p-8 text-center">
                <p className="text-slate-500 text-sm">
                  Click a finding in a clause to see full risk details here.
                </p>
              </div>
            )}

            {/* All risks summary */}
            {contract.risks.length > 0 && (
              <div className="glass-card p-5">
                <h3 className="text-sm font-semibold mb-3">All Findings</h3>
                <div className="space-y-2">
                  {contract.risks.map((risk) => (
                    <button
                      key={risk.id}
                      onClick={() => setSelectedRisk(risk)}
                      className={`w-full text-left p-3 rounded-xl text-sm transition-all ${
                        selectedRisk?.id === risk.id
                          ? "bg-blue-600/15 border border-blue-500/30"
                          : "bg-slate-800/30 hover:bg-slate-800/50 border border-transparent"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            {
                              CRITICAL: "bg-red-500",
                              HIGH: "bg-orange-500",
                              MEDIUM: "bg-yellow-500",
                              LOW: "bg-emerald-500",
                            }[risk.severity] || "bg-slate-500"
                          }`}
                        />
                        <span className="text-xs text-slate-500 uppercase">
                          {risk.risk_type.replace(/_/g, " ")}
                        </span>
                      </div>
                      <p className="text-slate-300 line-clamp-1">{risk.finding}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
