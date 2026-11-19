from tools.flight_tool import (
    clean_text,
    parse_route,
    resolve_location_to_iata,
    search_flights
)
from tools.tavily_tool import tavily_search
from backend import run_travel_agent

user_input = input("Enter travel request: ")

response = run_travel_agent(
    user_input=user_input,
    thread_id="test_user"
)

print("\nFINAL RESPONSE:\n")
print(response["answer"])