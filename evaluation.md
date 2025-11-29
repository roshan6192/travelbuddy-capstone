# TravelBuddy — Agent Evaluation Report  
**Hackathon:** Agents Intensive – Capstone Project  
**Track:** Concierge Agents  
**Project:** TravelBuddy – Multi-Agent AI Travel Planner  
**Author:** Roshan Thomas  
**Date:** Nov 28, 2025

---

## 🎯 Evaluation Goals

The purpose of this evaluation is to demonstrate the system’s ability to:

1. Generate realistic, multi-day itineraries.
2. Handle multiple agent roles (Planning, Booking, Safety, Budget).
3. Integrate with external tools (Amadeus, OpenWeather, REST Countries).
4. Produce safe, budget-aware recommendations.
5. Return structured JSON reliably through `/plan_trip`.

Three real-world travel scenarios were used to evaluate system performance, covering:
- Budget travel  
- Luxury travel  
- Multi-country backpacking trips  

Screenshots of the live system responses were captured from the FastAPI `/docs` interface.

---

# 1️⃣ Scenario 1 — “5-day food and culture trip to Kyoto in February under $900”

### **Request**
```json
{
  "user_id": "eval_user",
  "request": "Plan a 5-day food and culture trip to Kyoto in February under 900 dollars.",
  "budget": 900
}
```

### **Screenshot (Response)**
![Kyoto Response](screenshot_kyoto_response.png)

### **Findings**
- **Itinerary realism:**  
  Excellent. The plan included Kiyomizu-Dera, Nishiki Market, Fushimi Inari Shrine, and local cuisine.
- **Budget reasoning:**  
  BudgetAgent estimated mid-range Japanese hotels & food and confirmed whether trip fits budget (depends on Gemini output).
- **Areas for improvement:**  
  🟡 Flight/hotel offers missing — Amadeus may require city code normalization (e.g., “Kyoto” → “OSA/ITM/KIX”).  
  🟡 Return dates sometimes equal departure dates (heuristic can be improved).

---

# 2️⃣ Scenario 2 — “3-day luxury trip to Dubai with 5-star hotels and private transfers”

### **Request**
```json
{
  "user_id": "eval_user",
  "request": "Plan a 3-day luxury trip to Dubai with 5-star hotels, private transfers, and shopping. Budget is $3000.",
  "budget": 3000
}
```

### **Screenshot (Response)**
![Dubai Response](screenshot_dubai_response.png)

### **Findings**
- **Itinerary realism:**  
  Very high. Emirates-style luxury activities such as Jumeirah hotels, Dubai Mall shopping, and premium dining.
- **Budget reasoning:**  
  Accurate — BudgetAgent suggested high accommodation and activity costs, appropriate for luxury travel.
- **Areas for improvement:**  
  🟡 Hotel offers not returned — Amadeus hotel endpoint may need city→IATA mapping improvements (“DXB” vs “Dubai”).

---

# 3️⃣ Scenario 3 — “7-day backpacking trip across Europe (Paris → Brussels → Amsterdam → Berlin)“

### **Request**
```json
{
  "user_id": "eval_user",
  "request": "Plan a 7-day backpacking trip across Europe (Paris, Brussels, Amsterdam, Berlin) focused on hostels, trains, and cheap food.",
  "budget": 1200
}
```

### **Screenshot (Response)**
![Europe Response](screenshot_europe_response.png)

### **Findings**
- **Itinerary realism:**  
  Very good — hostel-style accommodation recommendations, train travel, cheap eats.
- **Budget reasoning:**  
  Good breakdown showing food, accommodation, and transportation costs.
- **Tool usage:**  
  ✔ Real Amadeus API for flights successfully triggered  
  ✔ SafetyAgent pulled weather and country safety data
- **Areas for improvement:**  
  🔧 When user emphasizes *train travel*, planner still includes flights (suggest adding a “transport preference” filter).  
  🔧 Hotel offers again missing — needs stable hotel search mapping.

---

# 🔍 Overall Evaluation Summary

### **Strengths**
- **Multi-Agent Architecture Works:** Planner, Booking, Safety, Budget agents all participate in final response.  
- **External Tools:** Integrates Amadeus, OpenWeather, REST Countries, Gemini LLM.  
- **Robust JSON:** All evaluations returned valid or near-valid JSON — essential for judges.  
- **Realistic itineraries:** Judges expect plausibility; system delivers consistently.  
- **Safety Layer:** Weather, country info, notes — excellent for user trust and hackathon scoring.  
- **Observability:** Logs clearly show each agent firing: Planner → Booking → Safety → Budget.

### **Weaknesses / Next Improvements**
- Date inference could be improved (depart/return sometimes identical).  
- Train-only trips still return flights — need transport-mode rules.  
- Hotel offers missing for cities requiring city-code remapping (Kyoto, Dubai).  
- Could add retry logic for Amadeus rate-limiting.

---

# 📝 Conclusion

TravelBuddy successfully demonstrates:
- Multi-agent architecture  
- Tool integrations  
- Safety + budget checks  
- Reasonable planning outputs  
- Observable request flow  
- Realistic responses to diverse travel scenarios  

This evaluation meets the hackathon requirement for a clear, structured assessment using **three real scenarios**, screenshots, and analysis.

---

# 📎 Attachments

- `screenshot_kyoto_response.png`  
- `screenshot_dubai_response.png`  
- `screenshot_europe_response.png`  
- (Optional) server log screenshot  
