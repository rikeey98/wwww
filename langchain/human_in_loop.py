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
    print("\n⏸️  Human review node (but already interrupted before this)")
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
    interrupt_before=["review"]  # review 직전에 멈춤
)

config = {"configurable": {"thread_id": "demo"}}

# ===== Step 1: Initial run (멈을 때까지 실행) =====
print("=" * 50)
print("STEP 1: Initial Draft Generation")
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

# ===== Step 2: Check state (멈춘 상태 확인) =====
print("\n" + "=" * 50)
print("STEP 2: Execution Paused - Check State")
print("=" * 50)

current = app.get_state(config)
print(f"\n📄 Current Draft:")
print(current.values['draft'])
print(f"\n⏭️  Next node to execute: {current.next}")

# ===== Step 3: Human decision =====
print("\n" + "=" * 50)
print("STEP 3: Human Decision")
print("=" * 50)

choice = input("\n👤 Approve this draft? (yes/no): ").strip().lower()

if choice == "yes":
    print("\n✅ Approving draft...")
    app.update_state(config, {"approved": True})
else:
    print("\n❌ Rejecting draft - requesting revision...")
    feedback = input("💬 Enter your feedback: ").strip()
    app.update_state(config, {
        "approved": False,
        "human_feedback": feedback or "Please improve"
    })

# ===== Step 4: Resume execution =====
print("\n" + "=" * 50)
print("STEP 4: Resuming Execution")
print("=" * 50)

result = app.invoke(None, config=config)

# Check if we need another round
current = app.get_state(config)
if current.next:  # Still has next node (멈춤)
    print("\n⏸️  Execution paused again!")
    print(f"📄 Revised Draft:")
    print(current.values['draft'])
    
    choice2 = input("\n👤 Approve this revised draft? (yes/no): ").strip().lower()
    
    if choice2 == "yes":
        app.update_state(config, {"approved": True})
    else:
        feedback2 = input("💬 Enter feedback: ").strip()
        app.update_state(config, {
            "approved": False,
            "human_feedback": feedback2 or "Please improve more"
        })
    
    print("\n" + "=" * 50)
    print("Resuming again...")
    print("=" * 50)
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
