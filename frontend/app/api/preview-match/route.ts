import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.json();

  const backendUrl = process.env.BACKEND_BASE_URL;
  if (!backendUrl) {
    return NextResponse.json(
      { error: "BACKEND_BASE_URL not set" },
      { status: 500 }
    );
  }

  const res = await fetch(`${backendUrl}/preview-match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
