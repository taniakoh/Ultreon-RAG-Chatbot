# Fullstack Developer — Take-Home Assignment

**Timeline:** 1-2 days  
**Submission:** GitHub repository link

---

## The Brief

You have been assigned to a new client project at UltreonAI. Below is the client's request. Read it carefully — your job is to interpret their needs and deliver a working solution.

---

### Client Request

> **From:** Sarah Tan, Managing Partner — TanLaw Advisory  
> **To:** UltreonAI Development Team
>
> Hi team,
>
> We're a 15-person legal consultancy based in Singapore. Our staff spend too much time searching through our internal documents — policy guides, procedures, HR templates — to find specific information. Keyword search doesn't work well because people phrase questions differently from how the documents are written.
>
> We'd like a simple internal search tool where our staff can:
>
> 1. **Type a question in plain English** (e.g., "How many days of annual leave do new staff get?")
> 2. **Get a clear, AI-generated answer** based on our actual documents — not generic AI responses
> 3. **See the relevant source passages** so they can verify the answer and read the full context
>
> We currently have 5 internal documents (policies, procedures, guides). These don't change often — maybe once a quarter at most.
>
> A few things that really matter to us:
>
> - **Accuracy is critical** — wrong information about our policies could cause real problems
> - Our staff need to be able to **trust the answers** by seeing exactly where the information came from
> - It should look **professional and clean** — this will be used daily by non-technical staff
> - The tool should **clearly tell users when it doesn't know something** rather than guessing
>
> We've attached our 5 internal documents for you to work with.
>
> Looking forward to seeing what you come up with.
>
> Best regards,  
> Sarah Tan

---

## What You Need to Build

A web application that allows users to ask natural language questions and receive AI-generated answers grounded in the provided documents.

### Core Requirements

1. **Search Interface** — A clean input where users type questions in natural language
2. **AI-Generated Answers** — Responses that are based on the content of the provided documents, not generic LLM knowledge
3. **Source Attribution** — Each answer must show which document(s) and passage(s) it drew from, so users can verify the information
4. **Honest Uncertainty** — When the documents don't contain relevant information, the tool should clearly say so rather than fabricating an answer

### Provided Documents

The `sample-documents/` folder contains 5 text files representing TanLaw Advisory's internal documents:

| Document | Content |
|----------|---------|
| `annual-leave-policy.txt` | Leave entitlements, application process, carry-over rules |
| `expense-claims-procedure.txt` | Claimable expenses, approval workflow, submission deadlines |
| `client-onboarding-guide.txt` | KYC requirements, engagement letters, onboarding steps |
| `office-guidelines.txt` | Working hours, remote work, dress code, meeting rooms |
| `data-protection-policy.txt` | PDPA compliance, data handling, breach response |

These documents should be pre-loaded into your application. File upload functionality is **not required**.

---

## What You Need to Deliver

### 1. GitHub Repository

A public or private GitHub repository containing your complete source code. The repository should include:

- **Working application** that runs locally
- **README** with:
  - Setup instructions (ideally a single command like `npm install && npm run dev`)
  - Your tech stack choices and **why you chose them** (brief justification, not an essay)
  - A short architecture overview — how the system works, how the pieces fit together
  - Any assumptions or tradeoffs you made

### 2. Running Application

Your application should run locally via a straightforward setup process. We will follow your README instructions to run it, so make sure they work.

### 3. Architecture Rationale

In your README (or a separate section), briefly explain:

- How you process and store the documents for retrieval
- How the retrieval pipeline works (how does a user question become an answer?)
- Your database schema and why you designed it that way
- Any tradeoffs you made and what you would do differently with more time

A diagram is welcome but not required — clear written explanation is sufficient.

---

## Tech Stack

**Your choice.** Use whatever tools, frameworks, and services you are most productive with. We care about your reasoning, not whether you picked our exact stack.

In your README, briefly justify your choices. There are no wrong answers — we want to understand your thinking.

---

## API Keys

We will provide you with a **rate-limited Openrouter API key** for this assignment. The key has a **$10USD spending limit**, which is more than sufficient to complete the assignment if used responsibly.

- Use the provided key via environment variables (e.g., a `.env` file) — never hardcode it in your source code
- Be mindful of token usage during development (avoid unnecessary large context calls in loops)
- If you prefer to use a different LLM provider (Anthropic, Google, etc.), you may use your own API key instead — just document this in your README
- The provided key will be deactivated after the assessment period

**NOTE** To access API key -> https://vault.ultreonai.com/#/send/SHQpzpuwS5yXk5q037sA4A/AXx1BgvzyEWcSsqHLRSzfw
> Password is your phone number (e.g.  12345678)

---

## AI Coding Tools

**We encourage the use of AI coding agents** such as Claude Code, OpenCode, Cursor, Copilot, or similar tools. In this role, you will use these tools daily — we want to see that you can use them effectively.

However:

- You must be able to **explain every part of your code** during the follow-up interview
- Be prepared to discuss **how you used the AI agent** — what prompts worked well, where you had to intervene or redirect
- During the interview, we will ask you to **make a small live modification** to your code to verify your understanding of the codebase

Using AI tools well is a skill. Using them without understanding the output is a risk. We are evaluating both.

---

## What Happens Next

After you submit your repository, we will schedule a **60-minute technical interview** where you will:

1. **Demo your application** — walk us through the working product
2. **Discuss your architecture** — explain your design decisions, database schema, and retrieval approach
3. **Walk through your code** — show us key files and how you structured the project
4. **Make a small live change** — we will give you a minor modification to implement on the spot
5. **Discuss tradeoffs** — what would you change, how would it scale, what would you do with more time

This is a conversation, not an interrogation. We want to understand how you think and work.

---

## Sample Questions to Test With

Here are some questions you can use to verify your application works correctly. We will test with these and others during the review.

**Basic questions (answer is in a single clear location):**
- "How many days of annual leave do new employees get?"
- "What is the expense claim limit for client dinners?"
- "What documents do I need for onboarding a corporate client?"
- "What should I do if I suspect a data breach?"
- "What is the dress code on Fridays?"
- "Who is the Data Protection Officer?"

**Questions requiring nuance (edge cases, exceptions, conditions):**
- "Can I work from home? What are the rules?"
- "Can a probationary employee take annual leave?"
- "What happens if I submit an expense claim 45 days late?"
- "Can I work from a cafe when working remotely?"
- "What is the hotel allowance for a business trip to Japan?"

**Questions spanning multiple documents:**
- "How long do we keep client files after the engagement ends?"
- "If I take a client to dinner, what's the limit and how do I submit the claim?"
- "I lost my access card — what should I do and how much will it cost?"

**Should acknowledge uncertainty (answers not in the documents):**
- "What is the company's revenue?"
- "How do I request a salary increase?"
- "What programming languages does the company use?"

---

## Evaluation Criteria

We evaluate your submission on:

| Criteria | What We Look For |
|----------|------------------|
| **Retrieval Quality** | Are answers grounded in the documents? Does it handle off-topic questions well? |
| **Architecture** | Clean separation of concerns, sensible data flow, justified decisions |
| **Database Design** | Appropriate schema, clear data modelling rationale |
| **Code Quality** | Readability, error handling, project structure |
| **UI Quality** | Professional, clean, usable by non-technical staff |
| **Client Consciousness** | Did you address what the client actually asked for and cared about? |

### Bonus Points (Not Required)

- Streaming AI responses to the UI
- Mobile-responsive layout
- Suggested/example questions for new users
- Document source highlighting or linking
- Any form of testing
- Deployed to a live URL

---

## Submission

Send your GitHub repository link to your recruiter contact by the agreed deadline. Make sure:

- [ ] The README has clear setup instructions
- [ ] The application runs locally following those instructions
- [ ] Your `.env.example` file shows which environment variables are needed (without actual key values)
- [ ] You have not committed any API keys or secrets to the repository

Good luck. We look forward to seeing your work.
