"use client";
import { useState } from "react";
import { previewMatch } from "../lib/api";

export default function Home() {
  const [cvText, setCvText] = useState("");
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);

  const [matchScore, setMatchScore] = useState<number | null>(null);
  const [overallScore, setOverallScore] = useState<number | null>(null); // 总分
  const [strengths, setStrengths] = useState<string[]>([]);
  const [gaps, setGaps] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [cvSkills, setCvSkills] = useState<string[]>([]);
  const [jdSkills, setJdSkills] = useState<string[]>([]);

  const [coverageRatio, setCoverageRatio] = useState<number | null>(null);
  const [coveredSkills, setCoveredSkills] = useState<string[]>([]);
  const [missingSkills, setMissingSkills] = useState<string[]>([]);

  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    setMatchScore(null);
    setOverallScore(null);
    setStrengths([]);
    setGaps([]);
    setSuggestions([]);
    setCvSkills([]);
    setJdSkills([]);

    setCoverageRatio(null);
    setCoveredSkills([]);
    setMissingSkills([]);

    try {
      const data = await previewMatch({
        cv_text: cvText,
        job_description: jdText,
      });

      // 正常从 API 赋值
      setMatchScore(data.match_score);
      setStrengths(data.strengths || []);
      setGaps(data.gaps || []);
      setSuggestions(data.suggestions || []);
      setCvSkills(data.cv_skills || []);
      setJdSkills(data.jd_skills || []);

      setCoverageRatio(data.coverage_ratio ?? null);
      setCoveredSkills(data.covered_skills || []);
      setMissingSkills(data.missing_skills || []);
      setOverallScore(data.overall_score ?? null);
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : "Something went wrong";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
        <h1 className="text-2xl font-semibold">
          JobFitCV · Match Preview (Proto)
        </h1>
        <p className="text-sm text-slate-300">输入简历和职位 JD，</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">CV 文本</label>
            <textarea
              className="w-full h-32 rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm"
              value={cvText}
              onChange={(e) => setCvText(e.target.value)}
              placeholder="Paste your CV text here..."
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Job Description 文本</label>
            <textarea
              className="w-full h-32 rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm"
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste the job description here..."
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium bg-emerald-500 disabled:opacity-60"
          >
            {loading ? "Analyzing..." : "Preview Match"}
          </button>
        </form>

        {error && <p className="text-sm text-red-400">Error: {error}</p>}

        {overallScore !== null && (
          <div className="border-t border-slate-800 pt-4 space-y-4">
            <div className="space-y-1">
              <p className="text-sm">
                Overall fit:{" "}
                <span className="font-semibold">
                  {(overallScore * 100).toFixed(1)}%
                </span>
              </p>

              {matchScore !== null && (
                <p className="text-xs text-slate-300">
                  Semantic match (LLM):{" "}
                  <span className="font-semibold">
                    {(matchScore * 100).toFixed(1)}%
                  </span>
                </p>
              )}

              {coverageRatio !== null && (
                <p className="text-xs text-slate-300">
                  Skill coverage (rules):{" "}
                  <span className="font-semibold">
                    {(coverageRatio * 100).toFixed(1)}%
                  </span>
                </p>
              )}
            </div>

            {strengths.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">Strengths</p>
                <ul className="list-disc list-inside text-sm text-slate-200">
                  {strengths.map((item, idx) => (
                    <li key={`strength-${idx}`}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {gaps.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">Gaps / Risks</p>
                <ul className="list-disc list-inside text-sm text-slate-200">
                  {gaps.map((item, idx) => (
                    <li key={`gap-${idx}`}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {suggestions.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">Suggestions</p>
                <ul className="list-disc list-inside text-sm text-slate-200">
                  {suggestions.map((item, idx) => (
                    <li key={`suggestion-${idx}`}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {cvSkills.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">CV Skills (parsed)</p>
                <div className="flex flex-wrap gap-2 text-xs text-slate-200">
                  {cvSkills.map((skill, idx) => (
                    <span
                      key={`cv-skill-${idx}`}
                      className="px-2 py-1 rounded-full bg-slate-800 border border-slate-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {jdSkills.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">JD Skills (parsed)</p>
                <div className="flex flex-wrap gap-2 text-xs text-slate-200">
                  {jdSkills.map((skill, idx) => (
                    <span
                      key={`jd-skill-${idx}`}
                      className="px-2 py-1 rounded-full bg-slate-800 border border-slate-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {coveredSkills.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">
                  Skills matched (intersection)
                </p>
                <div className="flex flex-wrap gap-2 text-xs text-emerald-200">
                  {coveredSkills.map((skill, idx) => (
                    <span
                      key={`covered-${idx}`}
                      className="px-2 py-1 rounded-full bg-emerald-900/40 border border-emerald-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {missingSkills.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">Missing skills (from JD)</p>
                <div className="flex flex-wrap gap-2 text-xs text-red-200">
                  {missingSkills.map((skill, idx) => (
                    <span
                      key={`missing-${idx}`}
                      className="px-2 py-1 rounded-full bg-red-900/40 border border-red-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
