import os
os.environ["OPENAI_API_KEY"] = "dummy"

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal

llm = ChatOpenAI(
    base_url="address/v1",
    model="Qwen3-32B",
    temperature=0.7,
    max_tokens=200
)

# State
class State(TypedDict):
    user_input: str
    intent: str
    needs_info: bool
    info_collected: str
    response: str

# Classify intent
def classify_intent(state: State) -> State:
    prompt = f"""Classify user intent:
- greeting: hello, hi, etc
- question: asking for information
- complaint: problem or issue

Input: {state['user_input']}

Respond with only the intent name."""
    
    response = llm.invoke(prompt)
    intent = response.content.strip().lower()
    print(f"Intent: {intent}")
    return {"intent": intent}

def route_intent(state: State) -> Literal["greeting", "question", "complaint"]:
    intent = state['intent']
    if "greet" in intent:
        return "greeting"
    elif "question" in intent:
        return "question"
    elif "complaint" in intent:
        return "complaint"
    else:
        return "question"  # default

# Handle greeting
def handle_greeting(state: State) -> State:
    response = llm.invoke("Respond friendly to: " + state['user_input'])
    return {"response": response.content}

# Check if need more info
def check_info_need(state: State) -> State:
    prompt = f"""Does this question need clarification?
Question: {state['user_input']}

Respond with YES or NO only."""
    
    response = llm.invoke(prompt)
    needs_info = "yes" in response.content.lower()
    print(f"Needs clarification: {needs_info}")
    return {"needs_info": needs_info}

def route_info_need(state: State) -> Literal["ask_info", "answer"]:
    return "ask_info" if state['needs_info'] else "answer"

def ask_for_info(state: State) -> State:
    return {"response": "Can you provide more details about your question?"}

def answer_question(state: State) -> State:
    response = llm.invoke("Answer this question: " + state['user_input'])
    return {"response": response.content}

def handle_complaint(state: State) -> State:
    prompt = f"Apologize and address this complaint: {state['user_input']}"
    response = llm.invoke(prompt)
    return {"response": response.content}

# Build Graph
graph = StateGraph(State)

graph.add_node("classify", classify_intent)
graph.add_node("greeting", handle_greeting)
graph.add_node("check_info", check_info_need)
graph.add_node("ask_info", ask_for_info)
graph.add_node("answer", answer_question)
graph.add_node("complaint", handle_complaint)

graph.set_entry_point("classify")

# Route by intent
graph.add_conditional_edges(
    "classify",
    route_intent,
    {
        "greeting": "greeting",
        "question": "check_info",
        "complaint": "complaint"
    }
)

# Route by info need
graph.add_conditional_edges(
    "check_info",
    route_info_need,
    {
        "ask_info": "ask_info",
        "answer": "answer"
    }
)

# All end
graph.add_edge("greeting", END)
graph.add_edge("ask_info", END)
graph.add_edge("answer", END)
graph.add_edge("complaint", END)

app = graph.compile()

# Test
test_inputs = [
    "Hello!",
    "What is Python?",
    "The service is not working!"
]

for inp in test_inputs:
    print(f"\n{'='*50}")
    print(f"User: {inp}")
    result = app.invoke({"user_input": inp})
    print(f"Bot: {result['response']}")
```

**흐름도**:
```
        [classify]
        /    |    \
  greeting  question  complaint
     |        |          |
    END  [check_info]   END
           /      \
      need_info   clear
         |          |
     [ask_info]  [answer]
         |          |
        END        END
