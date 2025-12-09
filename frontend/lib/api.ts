// frontend/lib/api.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export async function previewMatch(payload: any) {
  const res = await fetch(`${API_BASE_URL}/match/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}
