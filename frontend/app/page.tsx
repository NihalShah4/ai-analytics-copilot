"use client";

import { useState } from "react";
import { uploadCsv, getPreview, getProfile } from "./api";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [datasetId, setDatasetId] = useState<string>("");
  const [preview, setPreview] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [error, setError] = useState<string>("");

  async function handleUpload() {
    setError("");
    setPreview(null);
    setProfile(null);

    if (!file) {
      setError("Please select a CSV file first.");
      return;
    }

    try {
      const result = await uploadCsv(file);
      setDatasetId(result.dataset_id);
    } catch (e: any) {
      setError(e.message || "Upload failed.");
    }
  }

  async function handlePreview() {
    setError("");
    if (!datasetId) return;

    try {
      const result = await getPreview(datasetId, 5);
      setPreview(result);
    } catch (e: any) {
      setError(e.message || "Preview failed.");
    }
  }

  async function handleProfile() {
    setError("");
    if (!datasetId) return;

    try {
      const result = await getProfile(datasetId);
      setProfile(result);
    } catch (e: any) {
      setError(e.message || "Profile failed.");
    }
  }

  return (
    <main style={{ maxWidth: 900, margin: "40px auto", padding: 16, fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ fontSize: 24, marginBottom: 8 }}>AI Analytics Copilot (Starter)</h1>
      <p style={{ marginTop: 0, color: "#444" }}>
        Upload a CSV, then preview and profile it using the backend APIs.
      </p>

      <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 20 }}>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button onClick={handleUpload}>Upload</button>
      </div>

      {datasetId && (
        <div style={{ marginTop: 16, padding: 12, border: "1px solid #ddd", borderRadius: 6 }}>
          <div><strong>dataset_id:</strong> {datasetId}</div>
          <div style={{ marginTop: 10, display: "flex", gap: 10 }}>
            <button onClick={handlePreview}>Load Preview</button>
            <button onClick={handleProfile}>Load Profile</button>
          </div>
        </div>
      )}

      {error && (
        <div style={{ marginTop: 16, color: "crimson" }}>
          {error}
        </div>
      )}

      {preview && (
        <section style={{ marginTop: 24 }}>
          <h2 style={{ fontSize: 18 }}>Preview</h2>

          <div style={{ marginBottom: 8, color: "#444" }}>
            <strong>Shape:</strong> {preview.shape?.[0]} x {preview.shape?.[1]}
          </div>

          <div style={{ overflowX: "auto", border: "1px solid #ddd", borderRadius: 6 }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {preview.columns?.map((col: string) => (
                    <th
                      key={col}
                      style={{
                        textAlign: "left",
                        padding: "10px 12px",
                        borderBottom: "1px solid #ddd",
                        background: "#f6f6f6",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {preview.preview?.map((row: any, idx: number) => (
                  <tr key={idx}>
                    {preview.columns?.map((col: string) => (
                      <td
                        key={col}
                        style={{
                          padding: "10px 12px",
                          borderBottom: "1px solid #eee",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {row[col] !== undefined && row[col] !== null ? String(row[col]) : ""}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <details style={{ marginTop: 12 }}>
            <summary style={{ cursor: "pointer" }}>Show raw JSON</summary>
            <pre style={{ background: "#f6f6f6", padding: 12, borderRadius: 6, overflowX: "auto" }}>
              {JSON.stringify(preview, null, 2)}
            </pre>
          </details>
        </section>
      )}


      {profile && (
        <section style={{ marginTop: 24 }}>
          <h2 style={{ fontSize: 18 }}>Profile</h2>

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
            <div style={{ border: "1px solid #ddd", borderRadius: 6, padding: 12, minWidth: 180 }}>
              <div style={{ color: "#666", fontSize: 12 }}>Rows</div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{profile.shape?.[0]}</div>
            </div>

            <div style={{ border: "1px solid #ddd", borderRadius: 6, padding: 12, minWidth: 180 }}>
              <div style={{ color: "#666", fontSize: 12 }}>Columns</div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{profile.shape?.[1]}</div>
            </div>
          </div>

          {/* Missing values */}
          <h3 style={{ fontSize: 16, marginTop: 18 }}>Missing values</h3>
          <div style={{ overflowX: "auto", border: "1px solid #ddd", borderRadius: 6 }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #ddd", background: "#f6f6f6" }}>Column</th>
                  <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #ddd", background: "#f6f6f6" }}>Missing</th>
                  <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #ddd", background: "#f6f6f6" }}>Missing %</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(profile.missing || {})
                  .slice(0, 15)
                  .map(([col, stats]: any) => (
                    <tr key={col}>
                      <td style={{ padding: "10px 12px", borderBottom: "1px solid #eee", whiteSpace: "nowrap" }}>{col}</td>
                      <td style={{ padding: "10px 12px", borderBottom: "1px solid #eee" }}>{stats.missing_count}</td>
                      <td style={{ padding: "10px 12px", borderBottom: "1px solid #eee" }}>{stats.missing_pct}%</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {/* Numeric summary */}
          <h3 style={{ fontSize: 16, marginTop: 18 }}>Numeric summary</h3>
          {Object.keys(profile.numeric_summary || {}).length === 0 ? (
            <div style={{ color: "#666" }}>No numeric columns detected.</div>
          ) : (
            <div style={{ overflowX: "auto", border: "1px solid #ddd", borderRadius: 6 }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #ddd", background: "#f6f6f6" }}>Column</th>
                    <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #ddd", background: "#f6f6f6" }}>Count</th>
                    <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #ddd", background: "#f6f6f6" }}>Mean</th>
                    <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #ddd", background: "#f6f6f6" }}>Std</th>
                    <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #ddd", background: "#f6f6f6" }}>Min</th>
                    <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #ddd", background: "#f6f6f6" }}>Max</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(profile.numeric_summary).map(([col, s]: any) => (
                    <tr key={col}>
                      <td style={{ padding: "10px 12px", borderBottom: "1px solid #eee", whiteSpace: "nowrap" }}>{col}</td>
                      <td style={{ padding: "10px 12px", borderBottom: "1px solid #eee" }}>{s.count}</td>
                      <td style={{ padding: "10px 12px", borderBottom: "1px solid #eee" }}>{Number(s.mean).toFixed(3)}</td>
                      <td style={{ padding: "10px 12px", borderBottom: "1px solid #eee" }}>{s.std === null ? "" : Number(s.std).toFixed(3)}</td>
                      <td style={{ padding: "10px 12px", borderBottom: "1px solid #eee" }}>{s.min}</td>
                      <td style={{ padding: "10px 12px", borderBottom: "1px solid #eee" }}>{s.max}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Categorical top values */}
          <h3 style={{ fontSize: 16, marginTop: 18 }}>Top values (categorical)</h3>
          {Object.keys(profile.categorical_top_values || {}).length === 0 ? (
            <div style={{ color: "#666" }}>No categorical columns detected.</div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 12 }}>
              {Object.entries(profile.categorical_top_values).map(([col, items]: any) => (
                <div key={col} style={{ border: "1px solid #ddd", borderRadius: 6, padding: 12 }}>
                  <div style={{ fontWeight: 700, marginBottom: 8 }}>{col}</div>
                  <ul style={{ margin: 0, paddingLeft: 18 }}>
                    {items.slice(0, 5).map((it: any, i: number) => (
                      <li key={i}>
                        <span style={{ color: "#444" }}>{it.value ?? "null"}</span> ({it.count})
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          <details style={{ marginTop: 12 }}>
            <summary style={{ cursor: "pointer" }}>Show raw JSON</summary>
            <pre style={{ background: "#f6f6f6", padding: 12, borderRadius: 6, overflowX: "auto" }}>
              {JSON.stringify(profile, null, 2)}
            </pre>
          </details>
        </section>
      )}
    </main>
  );
}
