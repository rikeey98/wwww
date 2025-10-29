import os
os.environ["OPENAI_API_KEY"] = "dummy"

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Literal

# State
class State(TypedDict):
    task: str
    draft: str
    human_feedback: str
    approved: bool
    version: int

# Generate draft
def generate_draft(state: State) -> State:
    version = state['version'] + 1
    print(f"\n--- Generating Draft v{version} ---")
    
    if version == 1:
        draft = f"Draft proposal for: {state['task']}\n- Point 1\n- Point 2\n- Point 3"
    else:
        draft = f"Revised proposal for: {state['task']}\nAddressing: {state['human_feedback']}\n- Updated Point 1\n- Updated Point 2\n- Updated Point 3"
    
    print(f"Draft:\n{draft}")
    
    return {
        "draft": draft,
        "version": version
    }

# Wait for human approval (interrupt here)
def human_review(state: State) -> State:
    print("\n⏸️  Waiting for human review...")
    print("(This is where the workflow pauses)")
    return {}

# Check approval
def check_approval(state: State) -> Literal["approved", "revise"]:
    if state.get('approved', False):
        return "approved"
    else:
        return "revise"

# Final node
def finalize(state: State) -> State:
    print(f"\n✓ Draft approved! Final version: v{state['version']}")
    return {}

# Build Graph
graph = StateGraph(State)

graph.add_node("generate", generate_draft)
graph.add_node("review", human_review)
graph.add_node("finalize", finalize)

graph.set_entry_point("generate")
graph.add_edge("generate", "review")

graph.add_conditional_edges(
    "review",
    check_approval,
    {
        "approved": "finalize",
        "revise": "generate"  # Loop back
    }
)

graph.add_edge("finalize", END)

# Compile with checkpointer and interrupt
memory = MemorySaver()
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["review"]  # Pause before review!
)

config = {"configurable": {"thread_id": "human-1"}}

# Step 1: Start workflow
print("=== Step 1: Start Workflow ===")
result = app.invoke(
    {
        "task": "New feature proposal",
        "draft": "",
        "human_feedback": "",
        "approved": False,
        "version": 0
    },
    config=config
)

print("\n🛑 Workflow paused for human review")
print(f"Current draft:\n{result['draft']}")

# Simulate human review
print("\n=== Human Reviews Draft ===")
print("Options:")
print("1. Approve")
print("2. Request changes")

# Simulate: Request changes
print("\nHuman decision: Request changes")
print("Feedback: Please add more details")

# Step 2: Update state with human feedback
current_state = app.get_state(config)
app.update_state(
    config,
    {
        "human_feedback": "Please add more details",
        "approved": False
    }
)

# Step 3: Resume workflow
print("\n=== Step 2: Resume Workflow ===")
result = app.invoke(None, config=config)  # Continue from checkpoint

print("\n🛑 Workflow paused again for review")
print(f"Updated draft:\n{result['draft']}")

# Simulate: Approve this time
print("\n=== Human Reviews Again ===")
print("Human decision: Approve")

app.update_state(
    config,
    {"approved": True}
)

# Step 4: Final resume
print("\n=== Step 3: Final Resume ===")
result = app.invoke(None, config=config)

print("\n✓ Workflow completed!")
