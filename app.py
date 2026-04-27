from langchain_core.messages import HumanMessage
from graph import build_graph
from dotenv import load_dotenv
import state

load_dotenv()

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