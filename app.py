from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
import operator
from langchain_openai import ChatOpenAI

load_dotenv()

#State definition
class SupportState(TypedDict):
    """State for the support agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    should_escalate: bool
    issue_type: str
    user_tier: str  # "vip" or "standard"
    order_status: str
    tracking_id: Annotated[int, operator.add]
    sentiment: str
    discount_code: str
    message_to_user: str

# Routing functions
def route_by_tier(state: SupportState) -> str:
	"""Route based on user tier."""
	if state.get("user_tier") == "vip":
		return "vip_path"
	return "standard_path"


def offer_by_sentiment(state: SupportState) -> str:
	"""Route based on sentiment."""
	if "negative" in state.get("sentiment", ""):
		return "vip_discount_offer" # Offer VIP discount to unhappy customers irrespective of their tier
	if "positive" in state.get("sentiment", ""):
		return "thank_you_message"
	if "neutral" in state.get("sentiment", ""):
		return "survey_request"
	return "survey_request"

# Node functions
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

#	Graph construction
def build_graph():
    workflow = StateGraph(SupportState)

    # Add nodes
    workflow.add_node("check_tier", check_user_tier_node)
    workflow.add_node("check_sentiment", check_sentiment_node)
    workflow.add_node("vip_agent", vip_agent_node)
    workflow.add_node("standard_agent", standard_agent_node)
    workflow.add_node("give_vip_discount", give_vip_discount_node)
    workflow.add_node("thank_you", thank_you_node)
    workflow.add_node("survey_request", survey_request_node)
    workflow.set_entry_point("check_tier")
    workflow.add_conditional_edges("check_tier", 
                                   route_by_tier,
                                   {
                                       "vip_path": "vip_agent",
                                        "standard_path": "standard_agent"
                                   },
    )
    workflow.add_conditional_edges("check_sentiment",
                                   offer_by_sentiment,
                                   {
                                       "vip_discount_offer": "give_vip_discount",
                                        "thank_you_message": "thank_you",
                                        "survey_request": "survey_request"
                                   },
                                   )
    # Add edges
    workflow.add_edge("vip_agent","check_sentiment")
    workflow.add_edge("standard_agent", "check_sentiment")
    workflow.add_edge("give_vip_discount", END)
    workflow.add_edge("thank_you", END)
    workflow.add_edge("survey_request", END)

    return workflow.compile()


# Main function to run the graph
def main() -> None:
	graph = build_graph()

#vip customer, neutral sentiment
	print("=== VIP Customer with Neutral Sentiment ===")
	vip_result = graph.invoke({
		"messages": [HumanMessage(content="I'm a VIP customer, please check my order.")],
		"should_escalate": False,
		"issue_type": "",
		"user_tier": "",
		"order_status": "",
		"tracking_id": 1001,
		"sentiment": "",
		"discount_code": "",
		"message_to_user": "",
		"survey_request": ""
	})

	print("VIP result:", 
	   "User tier: " + vip_result.get("user_tier")+"\n",
	   "Escalte: "+ str(vip_result.get("should_escalate"))+"\n",
	   "Issue Type: "+vip_result.get("issue_type")+"\n",
	   "Order is " + vip_result.get("order_status") + "\n",
	   "Tracking ID: " + str(vip_result.get("tracking_id"))+ "\n",
	   vip_result.get("message_to_user"), vip_result.get("discount_code"))
	
	current_tracking_id = vip_result.get("tracking_id")

# Standard customer with neutral sentiment
	print("\n=== Standard Customer with Neutral Sentiment ===")
	standard_result = graph.invoke({
		"messages": [HumanMessage(content="Check my order status")],
		"should_escalate": False,
		"issue_type": "",
		"user_tier": "",
		"tracking_id": current_tracking_id,
		"order_status": "",
		"sentiment": "neutral",
		"discount_code": "",
		"message_to_user": ""
	})
	print("Standard result:", 
	   "User tier: " + standard_result.get("user_tier")+"\n",
	   "Escalte: "+ str(standard_result.get("should_escalate"))+"\n",
	   "Issue Type: "+standard_result.get("issue_type")+"\n",
	   " Order is " + standard_result.get("order_status") + "\n",
	   " with tracking ID: " + str(standard_result.get("tracking_id"))+ "\n",
	   standard_result.get("message_to_user"), standard_result.get("discount_code")) 
	
	current_tracking_id = standard_result.get("tracking_id")
	
	## standard angry customer
	print("\n=== Standard Customer with Negative Sentiment ===")
	standard_result = graph.invoke({
		"messages": [HumanMessage(content="I am extremely unhappy with the delay in my order!")],
		"should_escalate": False,
		"issue_type": "",
		"user_tier": "",
		"tracking_id": current_tracking_id,
		"order_status": "",
		"sentiment": "",
		"discount_code": "",
		"message_to_user": ""
	})
	print("Standard result:", 
	   "User tier: " + standard_result.get("user_tier")+"\n",
	   "Escalte: "+ str(standard_result.get("should_escalate"))+"\n",
	   "Issue Type: "+standard_result.get("issue_type")+"\n",
	   " Order is " + standard_result.get("order_status") + "\n",
	   " with tracking ID: " + str(standard_result.get("tracking_id"))
	   + "\n",
	   	standard_result.get("message_to_user"), standard_result.get("discount_code"))
	
	current_tracking_id = standard_result.get("tracking_id")
	
#Happy VIP customer	
	print("\n=== VIP Customer with Positive Sentiment ===")
	vip_result = graph.invoke({
		"messages": [HumanMessage(content="I am happy with your service last time! I am very happy with the service. Can you check my order?")],
		"should_escalate": False,
		"issue_type": "",
		"user_tier": "",
		"order_status": "",
		"tracking_id": current_tracking_id,
		"sentiment": "",
		"discount_code": "",
		"message_to_user": ""
	})
	print("VIP result:", 
	   "User tier: " + vip_result.get("user_tier")+"\n",
	   "Escalte: "+ str(vip_result.get("should_escalate"))+"\n",
	   "Issue Type: "+vip_result.get("issue_type")+"\n",
	   "Order is " + vip_result.get("order_status") + "\n",
	   "Tracking ID: " + str(vip_result.get("tracking_id"))+ "\n",
	   vip_result.get("message_to_user"), vip_result.get("discount_code"))


if __name__ == "__main__":
	main()