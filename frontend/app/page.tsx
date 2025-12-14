import Link from "next/link";

export default function Home() {
  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-4xl font-bold mb-4">
        Make your CV fit the job — in minutes
      </h1>

      <p className="text-gray-600 mb-8">
        Paste your CV and a job description. Get clear gaps, strengths, and suggestions.
      </p>

      <ol className="list-decimal list-inside text-gray-700 mb-8 space-y-1">
        <li>Paste CV</li>
        <li>Paste JD</li>
        <li>See match score & gaps</li>
      </ol>

      <Link
        href="/analyze"
        className="inline-block bg-black text-white px-6 py-3 rounded-md"
      >
        Try it now
      </Link>
    </main>
  );
}
