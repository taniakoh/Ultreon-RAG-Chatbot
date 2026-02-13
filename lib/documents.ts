import fs from "fs";
import path from "path";

export interface DocumentMeta {
  slug: string;
  title: string;
  reference: string;
  effectiveDate: string;
  lastRevised: string;
  approvedBy: string;
  nextReviewDate: string;
  dataProtectionOfficer?: string;
  description: string;
}

export interface DocumentSection {
  id: string;
  number: number;
  title: string;
  content: string;
}

export interface ParsedDocument {
  meta: DocumentMeta;
  sections: DocumentSection[];
}

const DOCUMENTS: Record<string, { file: string; description: string }> = {
  "annual-leave-policy": {
    file: "annual-leave-policy.txt",
    description:
      "Leave entitlements, application procedures, and absence management guidelines for all employees.",
  },
  "client-onboarding-guide": {
    file: "client-onboarding-guide.txt",
    description:
      "Standard procedures for onboarding new clients, including KYC, engagement letters, and fee structures.",
  },
  "data-protection-policy": {
    file: "data-protection-policy.txt",
    description:
      "Data protection obligations under Singapore's PDPA, covering collection, storage, breach management, and individual rights.",
  },
  "expense-claims-procedure": {
    file: "expense-claims-procedure.txt",
    description:
      "Guidelines for claimable business expenses, approval workflows, submission requirements, and reimbursement timelines.",
  },
  "office-guidelines": {
    file: "office-guidelines.txt",
    description:
      "Workplace policies covering working hours, remote work, office facilities, IT equipment, dress code, and security.",
  },
};

function parseDocument(slug: string, raw: string): ParsedDocument {
  const lines = raw.split("\n");
  const info = DOCUMENTS[slug];

  // Extract title from first line: "TanLaw Advisory — Title"
  const titleLine = lines[0] ?? "";
  const title = titleLine.includes("—")
    ? titleLine.split("—").slice(1).join("—").trim()
    : titleLine.trim();

  // Extract metadata block (lines 1-6ish, before the first === separator)
  let reference = "";
  let effectiveDate = "";
  let lastRevised = "";
  let approvedBy = "";
  let nextReviewDate = "";
  let dataProtectionOfficer: string | undefined;

  for (let i = 1; i < Math.min(lines.length, 10); i++) {
    const line = lines[i].trim();
    if (line.startsWith("===")) break;
    if (line.startsWith("Document Reference:"))
      reference = line.replace("Document Reference:", "").trim();
    if (line.startsWith("Effective Date:"))
      effectiveDate = line.replace("Effective Date:", "").trim();
    if (line.startsWith("Last Revised:"))
      lastRevised = line.replace("Last Revised:", "").trim();
    if (line.startsWith("Approved By:"))
      approvedBy = line.replace("Approved By:", "").trim();
    if (line.startsWith("Next Review Date:"))
      nextReviewDate = line.replace("Next Review Date:", "").trim();
    if (line.startsWith("Data Protection Officer:"))
      dataProtectionOfficer = line
        .replace("Data Protection Officer:", "")
        .trim();
  }

  // Extract sections
  const sections: DocumentSection[] = [];
  const sectionRegex = /^SECTION\s+(\d+)\s+[—–-]\s+(.+)$/;
  let currentSection: DocumentSection | null = null;
  let contentLines: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Skip separator lines
    if (trimmed.startsWith("===")) continue;
    if (trimmed === "END OF DOCUMENT") break;

    const match = trimmed.match(sectionRegex);
    if (match) {
      // Save previous section
      if (currentSection) {
        currentSection.content = contentLines.join("\n").trim();
        sections.push(currentSection);
      }
      currentSection = {
        id: `section-${match[1]}`,
        number: parseInt(match[1], 10),
        title: match[2].trim(),
        content: "",
      };
      contentLines = [];
    } else if (currentSection) {
      contentLines.push(line);
    }
  }

  // Push last section
  if (currentSection) {
    currentSection.content = contentLines.join("\n").trim();
    sections.push(currentSection);
  }

  return {
    meta: {
      slug,
      title,
      reference,
      effectiveDate,
      lastRevised,
      approvedBy,
      nextReviewDate,
      dataProtectionOfficer,
      description: info.description,
    },
    sections,
  };
}

function getDocumentsDir(): string {
  return path.join(process.cwd(), "sample-documents");
}

export function getAllDocuments(): DocumentMeta[] {
  const dir = getDocumentsDir();
  return Object.entries(DOCUMENTS).map(([slug, info]) => {
    const raw = fs.readFileSync(path.join(dir, info.file), "utf-8");
    const doc = parseDocument(slug, raw);
    return doc.meta;
  });
}

export function getDocument(slug: string): ParsedDocument | null {
  const info = DOCUMENTS[slug];
  if (!info) return null;
  const filePath = path.join(getDocumentsDir(), info.file);
  if (!fs.existsSync(filePath)) return null;
  const raw = fs.readFileSync(filePath, "utf-8");
  return parseDocument(slug, raw);
}

export function getDocumentSlugs(): string[] {
  return Object.keys(DOCUMENTS);
}
