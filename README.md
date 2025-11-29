✈️ TravelBuddy — AI Multi-Agent Travel Planner (Capstone Project)

Agents Intensive – Capstone Project
Author: Roshan Thomas
Track: Concierge Agents
License: CC-BY-SA 4.0

🚀 Elevator Pitch (Problem → Solution → Value)
🧩 Problem

Travel planning is fragmented and time-consuming. Real data (flights, hotels, safety info) lives in multiple disconnected websites, and creating a realistic travel plan requires hours of manual research.

💡 Solution

TravelBuddy is a multi-agent AI concierge system that intelligently coordinates:
✔ Trip planning
✔ Budget control
✔ Safety checks
✔ Real bookings using Amadeus API

Agents use the A2A (Agent-to-Agent) protocol, memory, and real tools to produce a structured, realistic, budget-respecting itinerary.

🎯 Value

Saves hours of manual trip research

Produces a realistic, safety-aware, bookable travel plan

Uses real APIs → always grounded in real-world data

Easy to integrate via a FastAPI backend

🧠 Key AI Concepts Implemented
Requirement	           Status	            Notes
Multi-agent system	    ✅	              Planner, Budget, Safety, Booking agents
Tools	                ✅	              Amadeus API, OpenWeather, REST Countries
Memory & sessions	    ✅	              session_store.json
Observability	        ✅	              Structured logs with timestamps
A2A Protocol	        ✅	              Coordinator routes messages intelligently
Deployment	             ✔                 Optional	Runs via FastAPI; can be deployed anywhere
Agent Evaluation	    ✅	              evaluation.md with screenshots

🏗 Architecture Overview
User Request
     │
     ▼
┌────────────────────┐
│  TravelBuddyCoordinator
│  (A2A Router + Memory)
└────────────────────┘
     │
     ├──> TripPlannerAgent (Gemini)
     │        └ generates itinerary + interprets dates & destinations
     │
     ├──> BookingAgent (Amadeus API)
     │        └ finds real flights + hotels
     │
     ├──> SafetyAgent (REST Countries + Weather)
     │        └ safety notes, travel advisories, weather
     │
     └──> BudgetAgent
              └ compares plan cost with budget

    Output returned as clean JSON, example:

    {
    "itinerary": [...],
    "flights": [...],
    "hotels": [...],
    "safety": [...],
    "budget_evaluation": "...",
    "final_summary": "..."
    }

⚙️ Setup Instructions
1️⃣ Clone the repo
git clone https://github.com/roshan6192/travelbuddy-capstone.git
cd travelbuddy-capstone

2️⃣ Create virtual environment
python -m venv .tbenv
.tbenv\Scripts\activate   

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Add .env

Create a file named .env:

AMADEUS_CLIENT_ID=xxxxxxxx
AMADEUS_CLIENT_SECRET=xxxxxxxx
OPENWEATHER_API_KEY=xxxxxxxx
GEMINI_API_KEY=xxxxxxxx

▶️ Run API Server

Start backend:

uvicorn main:app --reload

Try:

POST /plan_trip
{
  "request": "Plan a 5-day trip to Kyoto under 900 dollars",
  "budget": 900
}

🧪 Evaluation Summary

See evaluation.md for:

✔ 3 scenarios tested
✔ Raw outputs + screenshots
✔ What worked
✔ What needs improvement

Included screenshots for:

Kyoto

Dubai

Europe backpacking


🏁 Conclusion
TravelBuddy demonstrates:

Multi-Agent collaboration

Tool-augmented generation

Real external API integration

Structured reasoning

Safety + budget intelligence

Clear observability & JSON outputs

A fully working FastAPI agent system

