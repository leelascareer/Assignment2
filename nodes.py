from state import SupportState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def check_user_tier_node(state: SupportState):
    first_message = state["messages"][0].content.lower()
    if "vip" in first_message or "premium" in first_message:
        return {"user_tier": "vip"}
    else:
        return {"user_tier": "standard"}

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
system_message = SystemMessage( content=(
                "Identify the user's issue type based on their message. " \
                "Return one word for the issue type. If you can't identify, return 'general'. " \
            )
        )

def vip_agent_node(state: SupportState):
    """VIP path: fast lane, no escalation."""
    prompt = [system_message,
        HumanMessage(content=state["messages"][-1].content),
    ]

    response = llm.invoke(prompt)
    new_issue_type = response.content.strip().lower()
    return {
	    "should_escalate": False,
        "issue_type": new_issue_type,
        "tracking_id": 1,
        "order_status": "shipped"
	    }   

def standard_agent_node(state: SupportState):
    """Standard path: may escalate."""
    prompt = [system_message,
        HumanMessage(content=state["messages"][0].content),
    ]
    response = llm.invoke(prompt)
    new_issue_type = response.content.strip().lower()
    return {
		"should_escalate": True,
        "issue_type": new_issue_type,
        "messages": state["messages"],
        "tracking_id": 1 ,
        "order_status": "processing",
	}

def check_sentiment_node(state: SupportState):
    """Standard path: may escalate."""
    prompt = [SystemMessage(content=(
                "Analyze the sentiment of the user's message. " \
                "You MUST Return one word from the list:['positive', 'negative', 'neutral']."
                "If you can't identify, return 'neutral'."
            )),
        HumanMessage(content=state["messages"][-1].content),
    ]
    response = llm.invoke(prompt)
    sentiment = response.content.strip().lower()
    print("Determined sentiment:", sentiment)
    return {
        "sentiment": sentiment
	}

def give_vip_discount_node(state: SupportState):
    """Node to give VIP discount."""
    return {"discount_code": "VIP10",
            "message_to_user": "Sorry about your experience. "
            "We would like to offer you a 10% discount on your next purchase! "
            "For your next purchase use discount code :"}

def thank_you_node(state: SupportState):
    """Node to give thank you message."""
    return {"message_to_user": "Thank you for your feedback! We look forward to serving you again."}

def survey_request_node(state: SupportState):
    """Node to request survey."""
    return {"message_to_user": "We'd love to hear your feedback! Please take a moment to fill out our survey."}