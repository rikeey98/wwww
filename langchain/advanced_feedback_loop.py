import os
os.environ["OPENAI_API_KEY"] = "dummy"

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal, List

llm = ChatOpenAI(
    base_url="address/v1",
    model="Qwen3-32B",
    temperature=0.7,
    max_tokens=500
)

# State
class State(TypedDict):
    requirements: str
    code: str
    test_results: List[str]
    errors: List[str]
    attempts: int
    max_attempts: int
    all_tests_passed: bool

# Generate code
def write_code(state: State) -> State:
    attempts = state['attempts'] + 1
    
    print(f"\n--- Attempt {attempts}: Writing Code ---")
    
    if attempts == 1:
        prompt = f"Write a simple Python function: {state['requirements']}"
    else:
        prompt = f"""Previous code had errors: {', '.join(state['errors'])}

Requirements: {state['requirements']}
Previous code:
{state['code']}

Fix the errors and improve the code."""
    
    response = llm.invoke(prompt)
    code = response.content
    
    print(f"Generated code:\n{code[:200]}...")
    
    return {
        "code": code,
        "attempts": attempts
    }

# Test code
def test_code(state: State) -> State:
    print("\n--- Testing Code ---")
    
    # Simulate testing
    # In real scenario, would actually execute tests
    test_results = []
    errors = []
    
    # Simple checks
    if "def " not in state['code']:
        errors.append("No function definition found")
        test_results.append("FAIL: No function")
    else:
        test_results.append("PASS: Function defined")
    
    if "return" not in state['code']:
        errors.append("No return statement")
        test_results.append("FAIL: No return")
    else:
        test_results.append("PASS: Has return")
    
    all_passed = len(errors) == 0
    
    print(f"Tests: {', '.join(test_results)}")
    if errors:
        print(f"Errors: {', '.join(errors)}")
    
    return {
        "test_results": test_results,
        "errors": errors,
        "all_tests_passed": all_passed
    }

# Decision
def should_retry(state: State) -> Literal["retry", "success", "max_attempts"]:
    if state['all_tests_passed']:
        return "success"
    elif state['attempts'] >= state['max_attempts']:
        return "max_attempts"
    else:
        return "retry"

def success_node(state: State) -> State:
    print(f"\n✓ All tests passed! Attempts: {state['attempts']}")
    return {}

def failure_node(state: State) -> State:
    print(f"\n✗ Max attempts reached. Tests still failing.")
    return {}

# Build Graph
graph = StateGraph(State)

graph.add_node("write", write_code)
graph.add_node("test", test_code)
graph.add_node("success", success_node)
graph.add_node("failure", failure_node)

graph.set_entry_point("write")
graph.add_edge("write", "test")

graph.add_conditional_edges(
    "test",
    should_retry,
    {
        "retry": "write",      # Loop back to write
        "success": "success",
        "max_attempts": "failure"
    }
)

graph.add_edge("success", END)
graph.add_edge("failure", END)

app = graph.compile()

# Test
result = app.invoke({
    "requirements": "a function that adds two numbers",
    "code": "",
    "test_results": [],
    "errors": [],
    "attempts": 0,
    "max_attempts": 3,
    "all_tests_passed": False
})

print(f"\n{'='*50}")
print("Final Summary:")
print(f"Attempts: {result['attempts']}")
print(f"All tests passed: {result['all_tests_passed']}")
print(f"\nFinal code:\n{result['code']}")
