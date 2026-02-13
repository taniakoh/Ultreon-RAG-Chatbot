import { notFound } from "next/navigation";
import Link from "next/link";
import { getDocument, getDocumentSlugs } from "@/lib/documents";
import PageHeader from "@/components/page-header";

export function generateStaticParams() {
  return getDocumentSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const doc = getDocument(slug);
  if (!doc) return { title: "Not Found" };
  return {
    title: `${doc.meta.title} — TanLaw Advisory`,
    description: doc.meta.description,
  };
}

export default async function DocumentPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const doc = getDocument(slug);
  if (!doc) notFound();

  const { meta, sections } = doc;

  return (
    <div className="flex min-h-screen flex-col bg-stone-50">
      <PageHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-5 py-10">
        {/* Breadcrumb */}
        <div className="mb-6 flex items-center gap-2 text-xs text-stone-400">
          <Link
            href="/documents"
            className="transition-colors hover:text-stone-700"
          >
            Documents
          </Link>
          <span>/</span>
          <span className="text-stone-600">{meta.title}</span>
        </div>

        {/* Title */}
        <h1 className="font-heading text-2xl font-bold tracking-tight text-stone-900">
          {meta.title}
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-stone-500">
          {meta.description}
        </p>

        {/* Metadata card */}
        <div className="mt-6 rounded-xl border border-stone-200 bg-white p-5">
          <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-[11px] font-medium uppercase tracking-wider text-stone-400">
                Document Ref
              </dt>
              <dd className="mt-0.5 font-medium text-stone-700">
                {meta.reference}
              </dd>
            </div>
            <div>
              <dt className="text-[11px] font-medium uppercase tracking-wider text-stone-400">
                Effective Date
              </dt>
              <dd className="mt-0.5 text-stone-700">{meta.effectiveDate}</dd>
            </div>
            <div>
              <dt className="text-[11px] font-medium uppercase tracking-wider text-stone-400">
                Last Revised
              </dt>
              <dd className="mt-0.5 text-stone-700">{meta.lastRevised}</dd>
            </div>
            <div>
              <dt className="text-[11px] font-medium uppercase tracking-wider text-stone-400">
                Approved By
              </dt>
              <dd className="mt-0.5 text-stone-700">{meta.approvedBy}</dd>
            </div>
            <div>
              <dt className="text-[11px] font-medium uppercase tracking-wider text-stone-400">
                Next Review
              </dt>
              <dd className="mt-0.5 text-stone-700">{meta.nextReviewDate}</dd>
            </div>
            {meta.dataProtectionOfficer && (
              <div>
                <dt className="text-[11px] font-medium uppercase tracking-wider text-stone-400">
                  DPO
                </dt>
                <dd className="mt-0.5 text-stone-700">
                  {meta.dataProtectionOfficer}
                </dd>
              </div>
            )}
          </dl>
        </div>

        {/* Table of contents */}
        <nav className="mt-8 rounded-xl border border-stone-200 bg-white p-5">
          <h2 className="font-heading text-sm font-semibold text-stone-900">
            Contents
          </h2>
          <ol className="mt-3 space-y-1.5">
            {sections.map((section) => (
              <li key={section.id}>
                <a
                  href={`#${section.id}`}
                  className="text-sm text-stone-500 transition-colors hover:text-stone-900"
                >
                  <span className="mr-2 text-stone-400">
                    {section.number}.
                  </span>
                  {section.title}
                </a>
              </li>
            ))}
          </ol>
        </nav>

        {/* Sections */}
        <div className="mt-10 space-y-10">
          {sections.map((section) => (
            <section key={section.id} id={section.id}>
              <h2 className="font-heading border-b border-stone-200 pb-2 text-lg font-semibold text-stone-900">
                <span className="mr-2 text-stone-400">{section.number}.</span>
                {section.title}
              </h2>
              <div className="mt-4 text-sm leading-relaxed text-stone-700 whitespace-pre-line">
                {section.content}
              </div>
            </section>
          ))}
        </div>

        {/* Back link */}
        <div className="mt-12 border-t border-stone-200 pt-6">
          <Link
            href="/documents"
            className="text-sm font-medium text-stone-500 transition-colors hover:text-stone-900"
          >
            &larr; Back to all documents
          </Link>
        </div>
      </main>
    </div>
  );
}
