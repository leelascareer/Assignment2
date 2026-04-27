from state import SupportState


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

