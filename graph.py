from langgraph.graph import StateGraph, END
from state import SupportState
import routing as routing
import nodes as nodes
from dotenv import load_dotenv

load_dotenv()


def build_graph():
    workflow = StateGraph(SupportState)

    # Add nodes
    workflow.add_node("check_tier", nodes.check_user_tier_node)
    workflow.add_node("check_sentiment", nodes.check_sentiment_node)
    workflow.add_node("vip_agent", nodes.vip_agent_node)
    workflow.add_node("standard_agent", nodes.standard_agent_node)
    workflow.add_node("give_vip_discount", nodes.give_vip_discount_node)
    workflow.add_node("thank_you", nodes.thank_you_node)
    workflow.add_node("survey_request", nodes.survey_request_node)
    workflow.set_entry_point("check_tier")
    workflow.add_conditional_edges("check_tier", 
                                   routing.route_by_tier,
                                   {
                                       "vip_path": "vip_agent",
                                        "standard_path": "standard_agent"
                                   },
    )
    workflow.add_conditional_edges("check_sentiment",
                                   routing.offer_by_sentiment,
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