import Link from "next/link";
import { getAllDocuments } from "@/lib/documents";
import PageHeader from "@/components/page-header";

export const metadata = {
  title: "Policy Documents — TanLaw Advisory",
  description: "Browse TanLaw Advisory's internal policy documents.",
};

export default function DocumentsPage() {
  const documents = getAllDocuments();

  return (
    <div className="flex min-h-screen flex-col bg-stone-50">
      <PageHeader />
      <main className="mx-auto w-full max-w-4xl flex-1 px-5 py-10">
        <div className="mb-8">
          <h1 className="font-heading text-2xl font-bold tracking-tight text-stone-900">
            Policy Documents
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-stone-500">
            Internal policies and procedures for TanLaw Advisory staff.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {documents.map((doc) => (
            <Link
              key={doc.slug}
              href={`/documents/${doc.slug}`}
              className="group rounded-xl border border-stone-200 bg-white p-5 shadow-sm transition-all hover:border-stone-300 hover:shadow-md"
            >
              <div className="mb-2 flex items-center gap-2">
                <span className="rounded-md bg-stone-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-stone-500">
                  {doc.reference}
                </span>
              </div>
              <h2 className="font-heading text-base font-semibold text-stone-900 group-hover:text-stone-700">
                {doc.title}
              </h2>
              <p className="mt-1.5 text-xs leading-relaxed text-stone-500">
                {doc.description}
              </p>
              <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-stone-400">
                <span>Effective: {doc.effectiveDate}</span>
                <span>Revised: {doc.lastRevised}</span>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
