import os
os.environ["OPENAI_API_KEY"] = "dummy"

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal

llm = ChatOpenAI(
    base_url="address/v1",
    model="Qwen3-32B",
    temperature=0.7,
    max_tokens=300
)

# State
class State(TypedDict):
    task: str
    content: str
    feedback: str
    score: int
    attempts: int
    max_attempts: int
    target_score: int
    history: list

# Generate content
def generate_content(state: State) -> State:
    attempts = state['attempts'] + 1
    
    print(f"\n--- Attempt {attempts} ---")
    
    if attempts == 1:
        prompt = f"Write a short paragraph about: {state['task']}"
    else:
        prompt = f"""Previous attempt had issues: {state['feedback']}

Task: {state['task']}
Previous content: {state['content']}

Improve the content based on the feedback."""
    
    response = llm.invoke(prompt)
    new_content = response.content
    
    print(f"Generated content: {new_content[:100]}...")
    
    return {
        "content": new_content,
        "attempts": attempts
    }

# Evaluate content
def evaluate_content(state: State) -> State:
    prompt = f"""Evaluate this content on a scale of 1-10:

Content: {state['content']}

Provide:
1. Score (1-10)
2. Brief feedback

Format:
SCORE: X
FEEDBACK: your feedback here"""
    
    response = llm.invoke(prompt)
    evaluation = response.content
    
    # Parse score (simple extraction)
    score = 5  # default
    feedback = evaluation
    
    if "SCORE:" in evaluation:
        try:
            score_line = [line for line in evaluation.split('\n') if 'SCORE:' in line][0]
            score = int(''.join(filter(str.isdigit, score_line)))
        except:
            pass
    
    print(f"Score: {score}/10")
    print(f"Feedback: {feedback[:100]}...")
    
    return {
        "score": score,
        "feedback": feedback,
        "history": state['history'] + [{
            "attempt": state['attempts'],
            "score": score,
            "content": state['content'][:50] + "..."
        }]
    }

# Decision
def should_improve(state: State) -> Literal["improve", "done", "max_reached"]:
    if state['score'] >= state['target_score']:
        return "done"
    elif state['attempts'] >= state['max_attempts']:
        return "max_reached"
    else:
        return "improve"

def final_success(state: State) -> State:
    print(f"\n✓ Quality target reached! Score: {state['score']}/{state['target_score']}")
    return {}

def final_max(state: State) -> State:
    print(f"\n✗ Max attempts. Best score: {state['score']}/{state['target_score']}")
    return {}

# Build Graph
graph = StateGraph(State)

graph.add_node("generate", generate_content)
graph.add_node("evaluate", evaluate_content)
graph.add_node("success", final_success)
graph.add_node("max", final_max)

graph.set_entry_point("generate")
graph.add_edge("generate", "evaluate")

graph.add_conditional_edges(
    "evaluate",
    should_improve,
    {
        "improve": "generate",  # Loop back to generate!
        "done": "success",
        "max_reached": "max"
    }
)

graph.add_edge("success", END)
graph.add_edge("max", END)

app = graph.compile()

# Test
result = app.invoke({
    "task": "the benefits of exercise",
    "content": "",
    "feedback": "",
    "score": 0,
    "attempts": 0,
    "max_attempts": 3,
    "target_score": 8,
    "history": []
})

print(f"\n{'='*50}")
print("Final Result:")
print(f"Attempts: {result['attempts']}")
print(f"Final Score: {result['score']}")
print(f"\nFinal Content:\n{result['content']}")
