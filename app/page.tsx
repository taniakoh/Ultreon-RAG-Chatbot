"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import PageHeader from "@/components/page-header";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [messages.length === 0]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data = await res.json();

      let content = data.answer || "Sorry, I couldn't generate a response.";

      if (data.sources && data.sources.length > 0) {
        content += "\n\n---\n**Sources:**";
        for (const src of data.sources) {
          const score = src.score != null ? ` (relevance: ${(src.score * 100).toFixed(0)}%)` : "";
          content += `\n• **${src.document_name}**${score}\n  "${src.text.slice(0, 200)}${src.text.length > 200 ? "…" : ""}"`;
        }
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, something went wrong.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="flex min-h-screen flex-col bg-stone-50">
      {/* Top bar */}
      <PageHeader>
        {hasMessages && (
          <button
            onClick={() => setMessages([])}
            className="flex items-center gap-1.5 rounded-lg border border-stone-200 bg-white px-3 py-1.5 text-xs font-medium text-stone-600 shadow-sm transition-all hover:border-stone-300 hover:bg-stone-50 hover:text-stone-900 active:scale-[0.97]"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 16 16"
              fill="currentColor"
              className="h-3 w-3"
            >
              <path d="M3.75 2a.75.75 0 0 0-.75.75v10.5a.75.75 0 0 0 1.085.67L8 11.69l3.915 2.23A.75.75 0 0 0 13 13.25V2.75a.75.75 0 0 0-.75-.75h-8.5Z" />
            </svg>
            New chat
          </button>
        )}
      </PageHeader>

      {/* Chat area */}
      <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col px-5">
        {!hasMessages ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-5 pb-24 text-center">
            <div className="animate-hero-title flex flex-col items-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-stone-900 shadow-lg">
                <span className="text-xl font-bold text-white">T</span>
              </div>
              <h1 className="font-heading text-2xl font-semibold tracking-tight text-stone-900">
                TanLaw Advisory
              </h1>
            </div>
            <p className="animate-hero-subtitle max-w-xs text-sm leading-relaxed text-stone-500">
              Ask questions about internal policies, procedures, and guidelines.
            </p>
            <div className="animate-hero-input mt-2 flex flex-wrap items-center justify-center gap-2">
              {["Annual leave policy", "Expense claims", "Data protection"].map(
                (q) => (
                  <button
                    key={q}
                    onClick={() => setInput(q)}
                    className="rounded-full border border-stone-200 bg-white px-3.5 py-1.5 text-xs font-medium text-stone-600 shadow-sm transition-all hover:border-stone-300 hover:bg-stone-50 hover:text-stone-900 active:scale-[0.97] cursor-pointer"
                  >
                    {q}
                  </button>
                )
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-1 flex-col gap-5 overflow-y-auto py-6">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`animate-fade-in-up flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className="flex max-w-[85%] gap-3">
                  {msg.role === "assistant" && (
                    <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-stone-900">
                      <span className="text-[10px] font-bold text-white">
                        T
                      </span>
                    </div>
                  )}
                  <div
                    className={`rounded-2xl px-4 py-2.5 text-[13px] leading-relaxed whitespace-pre-wrap ${
                      msg.role === "user"
                        ? "rounded-br-md bg-stone-900 text-white"
                        : "rounded-bl-md bg-white text-stone-800 shadow-sm ring-1 ring-stone-200/60"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="animate-fade-in-up flex justify-start">
                <div className="flex max-w-[85%] gap-3">
                  <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-stone-900">
                    <span className="text-[10px] font-bold text-white">
                      T
                    </span>
                  </div>
                  <div className="loading-dots flex items-center gap-1.5 rounded-2xl rounded-bl-md bg-white px-4 py-3 shadow-sm ring-1 ring-stone-200/60">
                    <span className="text-stone-400" />
                    <span className="text-stone-400" />
                    <span className="text-stone-400" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Input */}
      <div
        className={`border-t border-stone-200/80 bg-white/70 px-5 py-4 backdrop-blur-xl ${!hasMessages ? "animate-hero-input border-t-0 bg-transparent" : ""}`}
      >
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex w-full max-w-2xl items-center gap-2"
        >
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about internal policies..."
              className="w-full rounded-xl border border-stone-300/80 bg-white py-3 pl-4 pr-12 text-sm text-black shadow-sm outline-none transition-all placeholder:text-stone-400 focus:border-stone-400 focus:ring-2 focus:ring-stone-200"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="cursor-pointer absolute right-1.5 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg bg-black text-white transition-all hover:bg-stone-700 disabled:opacity-30 active:scale-[0.92]"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="h-3.5 w-3.5"
              >
                <path d="M3.105 2.288a.75.75 0 0 0-.826.95l1.414 4.926A1.5 1.5 0 0 0 5.135 9.25h6.115a.75.75 0 0 1 0 1.5H5.135a1.5 1.5 0 0 0-1.442 1.086l-1.414 4.926a.75.75 0 0 0 .826.95l14.095-5.635a.75.75 0 0 0 0-1.392L3.105 2.288Z" />
              </svg>
            </button>
          </div>
        </form>
        <p className="mx-auto mt-2 max-w-2xl text-center text-[11px] text-stone-400">
          Answers are generated from internal documents only.
        </p>
      </div>
    </div>
  );
}
