from agent_client import ask_gemini

if __name__ == "__main__":
    user_input = "You are TravelBudddy, a travel planning assistant. Plan a 1-day trip in Paris for someone who likes art."
    reply = ask_gemini(user_input)
    print(reply)