"use client";

import { useAuth } from "@clerk/nextjs";
import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, type ContractListItem } from "../../../lib/api";
import {
  riskBgColor,
  statusBadgeClass,
  statusLabel,
  formatDate,
} from "../../../lib/utils";

export default function ContractsPage() {
  const { getToken } = useAuth();
  const [contracts, setContracts] = useState<ContractListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadContracts = useCallback(async () => {
    try {
      const token = await getToken();
      if (token) {
        const data = await api.listContracts(token);
        setContracts(data);
      }
    } catch (err) {
      console.error("Failed to load contracts:", err);
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    loadContracts();
  }, [loadContracts]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const token = await getToken();
      if (token) {
        await api.uploadContract(file, token);
        await loadContracts();
      }
    } catch (err) {
      console.error("Upload failed:", err);
      alert(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleUpload(file);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Contracts</h1>
      </div>

      {/* Upload dropzone */}
      <div
        className={`dropzone p-8 mb-8 text-center cursor-pointer transition-all ${
          dragActive ? "active" : ""
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          onChange={onFileSelect}
          className="hidden"
          id="contract-upload"
        />
        <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-2xl">
          {uploading ? "⏳" : "📤"}
        </div>
        <p className="text-slate-300 font-medium mb-1">
          {uploading ? "Uploading..." : "Drop a contract here or click to upload"}
        </p>
        <p className="text-sm text-slate-500">PDF or DOCX, up to 25MB</p>
      </div>

      {/* Contracts table */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass-card p-5">
              <div className="skeleton h-5 w-64 mb-2" />
              <div className="skeleton h-3 w-32" />
            </div>
          ))}
        </div>
      ) : contracts.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <p className="text-2xl mb-2">📄</p>
          <p className="text-slate-400">No contracts uploaded yet.</p>
          <p className="text-sm text-slate-500 mt-1">
            Upload your first contract to get started.
          </p>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Filename
                </th>
                <th className="text-left px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Upload Date
                </th>
                <th className="text-left px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="text-left px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Risk
                </th>
                <th className="text-right px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Score
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {contracts.map((c) => (
                <tr
                  key={c.id}
                  className="hover:bg-slate-800/30 transition-colors group cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <Link
                      href={`/contracts/${c.id}`}
                      className="text-sm font-medium group-hover:text-blue-400 transition-colors"
                    >
                      {c.filename}
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-400">
                    {formatDate(c.upload_date)}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-lg border ${statusBadgeClass(c.status)}`}
                    >
                      {statusLabel(c.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {c.risk_level ? (
                      <span
                        className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-lg border ${riskBgColor(c.risk_level)}`}
                      >
                        {c.risk_level}
                      </span>
                    ) : (
                      <span className="text-sm text-slate-500">—</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-mono">
                    {c.risk_score != null ? c.risk_score.toFixed(1) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
