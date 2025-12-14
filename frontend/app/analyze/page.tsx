"use client";

import { useState } from "react";
import Link from "next/link";

type PreviewMatchResponse = {
  match_score: number;
  strengths: string[];
  gaps: string[];
  suggestions: string[];
  cv_skills: string[];
  jd_skills: string[];
};

export default function AnalyzePage() {
  const [cvText, setCvText] = useState("");
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PreviewMatchResponse | null>(null);

  async function analyze() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("/api/preview-match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cv_text: cvText, jd_text: jdText }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data?.error ?? "Request failed");
        setLoading(false);
        return;
      }

      setResult(data);
    } catch (e) {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-semibold">Analyze CV vs Job</h1>
        <Link href="/" className="text-sm underline">
          Back
        </Link>
      </div>

      <div className="grid gap-4">
        <textarea
          className="w-full border rounded-md p-3 min-h-[140px]"
          placeholder="Paste your CV here"
          value={cvText}
          onChange={(e) => setCvText(e.target.value)}
        />
        <textarea
          className="w-full border rounded-md p-3 min-h-[140px]"
          placeholder="Paste the job description here"
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
        />

        <div className="flex gap-3 items-center">
          <button
            onClick={analyze}
            disabled={loading}
            className="bg-black text-white px-5 py-2 rounded-md disabled:opacity-50"
          >
            {loading ? "Analyzing…" : "Analyze"}
          </button>

          <span className="text-sm text-gray-600">
            Tip: keep it short for MVP (2–3 paragraphs each).
          </span>
        </div>
      </div>

      {error && (
        <div className="mt-6 border rounded-md p-4">
          <div className="font-semibold">Error</div>
          <div className="text-sm text-gray-700">{error}</div>
        </div>
      )}

      {result && (
        <section className="mt-8 grid gap-6">
          <div className="border rounded-md p-4">
            <div className="text-sm text-gray-600">Match Score</div>
            <div className="text-3xl font-bold">{result.match_score}</div>
          </div>

          <div className="border rounded-md p-4">
            <h2 className="font-semibold mb-2">Strengths</h2>
            <ul className="list-disc list-inside space-y-1">
              {result.strengths.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
          </div>

          <div className="border rounded-md p-4">
            <h2 className="font-semibold mb-2">Gaps</h2>
            <ul className="list-disc list-inside space-y-1">
              {result.gaps.map((g) => (
                <li key={g}>{g}</li>
              ))}
            </ul>
          </div>

          <div className="border rounded-md p-4">
            <h2 className="font-semibold mb-2">Suggestions</h2>
            <ul className="list-disc list-inside space-y-1">
              {result.suggestions.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
          </div>
        </section>
      )}
    </main>
  );
}

