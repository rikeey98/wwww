import os
os.environ["OPENAI_API_KEY"] = "dummy"

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict

# State
class State(TypedDict):
    messages: list
    step: int

# Nodes
def step_1(state: State) -> State:
    print("Executing Step 1...")
    return {
        "messages": state['messages'] + ["Step 1 completed"],
        "step": 1
    }

def step_2(state: State) -> State:
    print("Executing Step 2...")
    return {
        "messages": state['messages'] + ["Step 2 completed"],
        "step": 2
    }

def step_3(state: State) -> State:
    print("Executing Step 3...")
    return {
        "messages": state['messages'] + ["Step 3 completed"],
        "step": 3
    }

# Build Graph with checkpointer
graph = StateGraph(State)

graph.add_node("step_1", step_1)
graph.add_node("step_2", step_2)
graph.add_node("step_3", step_3)

graph.set_entry_point("step_1")
graph.add_edge("step_1", "step_2")
graph.add_edge("step_2", "step_3")
graph.add_edge("step_3", END)

# Add memory checkpointer
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# Configuration with thread_id
config = {"configurable": {"thread_id": "1"}}

# Run step by step
print("=== Run 1: Execute all steps ===")
result = app.invoke(
    {"messages": [], "step": 0},
    config=config
)

print(f"\nMessages: {result['messages']}")
print(f"Current step: {result['step']}")

# Get state history
print("\n=== Checkpoint History ===")
state_history = list(app.get_state_history(config))
print(f"Total checkpoints: {len(state_history)}")

for i, state_snapshot in enumerate(state_history):
    print(f"\nCheckpoint {i}:")
    print(f"  Step: {state_snapshot.values.get('step', 'N/A')}")
    print(f"  Messages: {state_snapshot.values.get('messages', [])}")

# Resume from specific checkpoint
print("\n=== Resume from Step 1 ===")
# Get checkpoint after step 1
checkpoint_id = state_history[2].config["configurable"]["checkpoint_id"]
print(f"Resuming from checkpoint: {checkpoint_id}")

# Continue from that point
config_resume = {
    "configurable": {
        "thread_id": "1",
        "checkpoint_id": checkpoint_id
    }
}

# Note: This continues from the checkpoint
