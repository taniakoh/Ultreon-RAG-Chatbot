import pytest
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator
from backend.engine import get_query_engine # Import your specific engine logic

# 1. Setup Fixtures (Shared resources)
@pytest.fixture(scope="module")
def query_engine():
    """Initializes the RAG engine once for all tests"""
    return get_query_engine()

@pytest.fixture(scope="module")
def faithfulness_eval():
    """Judge if the answer is based ONLY on the documents"""
    return FaithfulnessEvaluator()

@pytest.fixture(scope="module")
def relevancy_eval():
    """Judge if the answer actually addresses the user's question"""
    return RelevancyEvaluator()

# 2. Define your "Testing Questions" from Sarah's brief
# You can include 'expected_pass' to mark which ones should 'I don't know'
test_cases = [
    ("How many days of annual leave do new employees get?", True),
    ("What is the expense claim limit for client dinners?", True),
    ("Who is the Data Protection Officer?", True),
    ("What is the company's revenue?", False), # Should trigger 'I don't know' (Fail faithfulness check)
]

# 3. The Actual Test Function
@pytest.mark.parametrize("question, should_find_answer", test_cases)
def test_rag_accuracy(question, should_find_answer, query_engine, faithfulness_eval, relevancy_eval):
    # Get the AI response
    response = query_engine.query(question)
    
    # Run the Evaluators (LLM-as-a-judge)
    faith_result = faithfulness_eval.evaluate_response(response=response)
    rel_result = relevancy_eval.evaluate_response(query=question, response=response)

    if should_find_answer:
        # If an answer should exist, it must be faithful and relevant
        assert faith_result.passing, f"Hallucination detected for: {question}"
        assert rel_result.passing, f"Answer not relevant for: {question}"
    else:
        # If no answer exists, faithfulness might 'fail' (which is good)
        # as it means the bot didn't find supporting context and hopefully said "I don't know"
        assert not faith_result.pa