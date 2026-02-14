import pytest
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator
from backend.engine import build_query_engine


# 1. Setup Fixtures (Shared resources)
@pytest.fixture(scope="module")
def query_engine():
    """Initializes the RAG engine once for all tests"""
    return build_query_engine()


@pytest.fixture(scope="module")
def faithfulness_eval():
    """Judge if the answer is based ONLY on the documents"""
    return FaithfulnessEvaluator()


@pytest.fixture(scope="module")
def relevancy_eval():
    """Judge if the answer actually addresses the user's question"""
    return RelevancyEvaluator()


# 2. Test cases organized by category

# Basic questions — answer is in a single clear location
basic_cases = [
    ("How many days of annual leave do new employees get?", True),
    ("What is the expense claim limit for client dinners?", True),
    ("What documents do I need for onboarding a corporate client?", True),
    ("What should I do if I suspect a data breach?", True),
    ("What is the dress code on Fridays?", True),
    ("Who is the Data Protection Officer?", True),
]

# Questions requiring nuance — edge cases, exceptions, conditions
nuance_cases = [
    ("Can I work from home? What are the rules?", True),
    ("Can a probationary employee take annual leave?", True),
    ("What happens if I submit an expense claim 45 days late?", True),
    ("Can I work from a cafe when working remotely?", True),
    ("What is the hotel allowance for a business trip to Japan?", True),
]

# Questions spanning multiple documents
multi_doc_cases = [
    ("How long do we keep client files after the engagement ends?", True),
    ("If I take a client to dinner, what's the limit and how do I submit the claim?", True),
    ("I lost my access card — what should I do and how much will it cost?", True),
]

# Out-of-scope questions — should trigger "I don't know"
out_of_scope_cases = [
    ("What is the company's revenue?", False),
    ("What is the meaning of life?", False),
]

all_cases = basic_cases + nuance_cases + multi_doc_cases + out_of_scope_cases


# 3. The Actual Test Functions

@pytest.mark.parametrize("question, should_find_answer", basic_cases, ids=[q[:50] for q, _ in basic_cases])
def test_basic_questions(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval):
    """Basic questions where the answer is in a single clear location"""
    _run_rag_test(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval)


@pytest.mark.parametrize("question, should_find_answer", nuance_cases, ids=[c.values[0][:50] if hasattr(c, "values") else c[0][:50] for c in nuance_cases])
def test_nuance_questions(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval):
    """Questions requiring nuance — edge cases, exceptions, conditions"""
    _run_rag_test(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval)


@pytest.mark.parametrize("question, should_find_answer", multi_doc_cases, ids=[q[:50] for q, _ in multi_doc_cases])
def test_multi_doc_questions(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval):
    """Questions spanning multiple documents"""
    _run_rag_test(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval)


@pytest.mark.parametrize("question, should_find_answer", out_of_scope_cases, ids=[q[:50] for q, _ in out_of_scope_cases])
def test_out_of_scope_questions(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval):
    """Out-of-scope questions — should refuse to answer"""
    _run_rag_test(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval)


def _run_rag_test(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval):
    """Shared test logic for all RAG accuracy tests"""
    response = query_engine.query(question)

    # Run the Evaluators (LLM-as-a-judge)
    faith_result = faithfulness_eval.evaluate_response(response=response)
    rel_result = relevancy_eval.evaluate_response(query=question, response=response)

    if should_find_answer:
        # Answer should exist and must be faithful and relevant
        assert faith_result.passing, f"Hallucination detected for: {question}"
        assert rel_result.passing, f"Answer not relevant for: {question}"
    else:
        # Out-of-scope: the bot should refuse / say "I don't know"
        answer = str(response).lower()
        refusal_phrases = [
            "don't have enough information",
            "not covered in",
            "no relevant information",
            "i don't know",
            "not mentioned in the",
            "unable to find",
        ]
        refused = any(phrase in answer for phrase in refusal_phrases)
        assert refused, f"Should have refused but answered: {question}\nResponse: {response}"
