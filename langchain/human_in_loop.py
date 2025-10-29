from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Literal

class State(TypedDict):
    task: str
    draft: str
    human_feedback: str
    approved: bool
    version: int

def generate_draft(state: State) -> State:
    version = state['version'] + 1
    print(f"\n--- Generating Draft v{version} ---")
    
    if version == 1:
        draft = f"Draft proposal for: {state['task']}\n- Point 1\n- Point 2\n- Point 3"
    else:
        draft = f"Revised proposal for: {state['task']}\nAddressing: {state['human_feedback']}\n- Updated Point 1\n- Updated Point 2\n- Updated Point 3"
    
    print(f"Draft:\n{draft}")
    return {"draft": draft, "version": version}

def human_review(state: State) -> State:
    print("\n⏸️  Human review node")
    return {}

def check_approval(state: State) -> Literal["approved", "revise"]:
    return "approved" if state.get('approved', False) else "revise"

def finalize(state: State) -> State:
    print(f"\n✅ Draft approved! Final version: v{state['version']}")
    return {}

# Build graph
graph = StateGraph(State)
graph.add_node("draft", generate_draft)
graph.add_node("review", human_review)
graph.add_node("finalize", finalize)

graph.set_entry_point("draft")
graph.add_edge("draft", "review")
graph.add_conditional_edges("review", check_approval, {"approved": "finalize", "revise": "draft"})
graph.add_edge("finalize", END)

# Compile with interrupt
memory = MemorySaver()
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["review"]
)

config = {"configurable": {"thread_id": "demo"}}

# ===== Initial run =====
print("=" * 50)
print("Initial Draft Generation")
print("=" * 50)

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

# ===== Loop until approved =====
while True:
    current = app.get_state(config)
    
    # Check if finished
    if not current.next:
        print("\n✅ Workflow completed!")
        break
    
    # Show current draft
    print("\n" + "=" * 50)
    print(f"Draft v{current.values['version']}")
    print("=" * 50)
    print(f"\n📄 Current Draft:")
    print(current.values['draft'])
    
    # Get human decision
    choice = input("\n👤 Approve this draft? (yes/no): ").strip().lower()
    
    if choice == "yes":
        print("\n✅ Approving draft...")
        app.update_state(config, {"approved": True})
    else:
        print("\n❌ Requesting revision...")
        feedback = input("💬 Enter your feedback: ").strip()
        app.update_state(config, {
            "approved": False,
            "human_feedback": feedback or "Please improve"
        })
    
    # Resume execution
    print("\n⏩ Resuming...")
    result = app.invoke(None, config=config)

# ===== Final State =====
print("\n" + "=" * 50)
print("FINAL STATE")
print("=" * 50)

final = app.get_state(config)
print(f"\n📋 Task: {final.values['task']}")
print(f"📄 Final Draft:")
print(final.values['draft'])
print(f"🔢 Version: v{final.values['version']}")
print(f"✅ Approved: {final.values['approved']}")
