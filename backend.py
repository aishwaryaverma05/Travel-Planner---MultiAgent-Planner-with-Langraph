
import os
import certifi
import uuid

from dotenv import load_dotenv
load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from typing import TypedDict, Annotated
import operator

import psycopg
from psycopg.rows import dict_row

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
)

from langchain_groq import ChatGroq

from mcp_client import (
    tavily_mcp_search,
    aviation_mcp_call,
    extract_destination,
    forecast_mcp_search,
    weather_mcp_search,
)


# =========================
# Database Configuration
# =========================

def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL is missing. Please add your PostgreSQL URL to .env"
        )

    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"

    return database_url


# =========================
# API Keys
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env")


# =========================
# LLM Configuration
# =========================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=GROQ_API_KEY,
    max_tokens=900
)


# =========================
# Travel State
# =========================

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int
    weather_results: str


# =========================
# Flight Agent
# =========================

async def flight_agent(state: TravelState):

    print("\nINSIDE FLIGHT AGENT\n")

    try:
        airports = await aviation_mcp_call("list_airports")

        airlines = await aviation_mcp_call("list_airlines")

        # Limit API response size
        airport_data = str(airports)[:1000]
        airline_data = str(airlines)[:1000]

        flight_data = f"""
Airport Information:
{airport_data}

Airline Information:
{airline_data}

Note: These are airport and airline reference details.
Live flight availability and ticket prices are not confirmed.
"""

    except Exception as e:
        flight_data = f"Flight information unavailable: {str(e)[:300]}"

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight information fetched.")
        ]
    }


# =========================
# Hotel Agent
# =========================

async def hotel_agent(state: TravelState):

    print("\nINSIDE HOTEL AGENT\n")

    query = f"Best hotels for {state['user_query']}"

    try:
        hotel_results = await tavily_mcp_search(query)

        # Limit hotel search results
        hotel_results = str(hotel_results)[:1800]

    except Exception as e:
        hotel_results = f"Hotel information unavailable: {str(e)[:300]}"

    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched.")
        ]
    }


# =========================
# Weather Agent
# =========================

async def weather_agent(state: TravelState):

    print("\nINSIDE WEATHER AGENT\n")

    try:
        city = extract_destination(state["user_query"])

        weather_data = await weather_mcp_search(city)

        forecast_data = await forecast_mcp_search(city)

        # Limit weather response size
        weather_data = str(weather_data)[:700]
        forecast_data = str(forecast_data)[:700]

        weather_results = f"""
Current Weather:
{weather_data}

Forecast:
{forecast_data}
"""

    except Exception as e:
        weather_results = f"Weather information unavailable: {str(e)[:300]}"

    return {
        "weather_results": weather_results,
        "messages": [
            AIMessage(content="Weather information fetched.")
        ]
    }


# =========================
# Itinerary Agent
# =========================

async def itinerary_agent(state: TravelState):

    print("\nINSIDE ITINERARY AGENT\n")

    prompt = f"""
You are an expert AI travel planner.

Create a practical and budget-aware travel plan.

USER REQUEST:
{state['user_query'][:700]}

FLIGHT INFORMATION:
{state['flight_results'][:1200]}

HOTEL INFORMATION:
{state['hotel_results'][:1800]}

WEATHER INFORMATION:
{state['weather_results'][:1400]}

Prepare the final response using these sections:

1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Weather Information
5. Day-by-Day Itinerary
6. Estimated Budget
7. Final Recommendations

IMPORTANT:
- Give practical travel suggestions.
- Do not invent live flight availability or ticket prices.
- Clearly mention when flight prices or availability are unavailable.
- Do not invent hotel prices or ratings.
- Use the available weather information.
- If information is unavailable, clearly say so.
- Keep the response concise and useful.
"""

    response = await llm.ainvoke(
        [
            HumanMessage(content=prompt)
        ]
    )

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================
# Final Response Agent
# =========================

async def final_agent(state: TravelState):

    print("\nINSIDE FINAL AGENT\n")

    # Itinerary Agent already generates the complete final response.
    # No additional LLM call is needed.

    return {
        "messages": [
            AIMessage(content=state["itinerary"])
        ]
    }


# =========================
# Build LangGraph
# =========================

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("weather_agent", weather_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "weather_agent")
graph.add_edge("weather_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


# =========================
# PostgreSQL Async Checkpointer
# =========================

DATABASE_URL = get_database_url()

_conn = None
checkpointer = None
travel_graph = None


async def initialize_travel_graph():

    global _conn, checkpointer, travel_graph

    _conn = await psycopg.AsyncConnection.connect(
        DATABASE_URL,
        autocommit=True,
        row_factory=dict_row
    )

    checkpointer = AsyncPostgresSaver(_conn)

    await checkpointer.setup()

    travel_graph = graph.compile(
        checkpointer=checkpointer
    )

    print("\nTravel Graph Initialized Successfully\n")


async def close_travel_graph():

    global _conn, checkpointer, travel_graph

    if _conn is not None:
        await _conn.close()

    _conn = None
    checkpointer = None
    travel_graph = None

    print("\nTravel Graph Connection Closed\n")


# =========================
# Function for FastAPI
# =========================

async def run_travel_agent(
    user_input: str,
    thread_id: str | None = None
):

    if travel_graph is None:
        raise RuntimeError(
            "Travel graph is not initialized. Check FastAPI lifespan."
        )

    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await travel_graph.ainvoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "weather_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    final_answer = result["messages"][-1].content

    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "weather_results": result.get("weather_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0),
    }
