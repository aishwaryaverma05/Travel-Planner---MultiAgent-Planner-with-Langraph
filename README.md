# TripMate AI — Multi-Agent Travel Planner

An open-source AI travel planner that turns a natural-language trip request into a practical, budget-aware travel plan with flight guidance, hotel ideas, live weather forecasts, and a day-by-day itinerary. The system uses a dynamic multi-agent workflow built with **LangGraph**, **LangChain**, **Model Context Protocol (MCP)**, and **FastAPI**.

## Why This Project?

Planning a trip usually requires jumping across multiple websites, tools, and spreadsheets. **TripMate AI** brings that workflow into one place by combining intelligent routing, input safety guardrails, live MCP tool integrations, and human-in-the-loop review:

- **Supervisor Agent & Input Guardrails**: Validates travel-related intent, extracts trip constraints, and dynamically routes requests only to the necessary specialist agents.
- **Flight Agent**: Provides airport, airline, route, and fare guidance via AviationStack MCP.
- **Hotel Agent**: Researches accommodation and neighborhood recommendations via Tavily MCP.
- **Weather Agent**: Fetches current weather and forecasts through a custom local FastMCP server powered by OpenWeather.
- **Budget Agent**: Evaluates trip affordability, cost categories, and money-saving tips.
- **Itinerary Agent**: Synthesizes specialist outputs into a structured draft itinerary.
- **Human-in-the-Loop (HITL) Approval**: Pauses execution using LangGraph `interrupt()` so the user can approve the draft or submit revision feedback before finalizing.
- **Final Response Agent**: Produces a polished, structured Markdown travel plan incorporating user feedback.

## Features

- **Dynamic Multi-Agent Orchestration** with LangGraph (`StateGraph`)
- **Input Guardrail Validation** to filter non-travel or unsafe queries
- **Human-in-the-Loop (HITL) Workflow** (`interrupt` & `Command` resume) for draft review and revisions
- **MCP Integration (`MultiServerMCPClient`)** connecting remote and local MCP servers
- **Custom Weather MCP Server (`FastMCP`)** for real-time weather and forecasts via OpenWeather
- **Async PostgreSQL State Persistence** (`AsyncPostgresSaver`) for thread-based session continuity
- **Interactive Web UI & Export** with FastAPI, Jinja2, Markdown rendering, one-click copy, and PDF export
- **Fast LLM Inference** powered by Groq

## Tech Stack

- **Backend & AI:** Python 3.10+, FastAPI, LangGraph, LangChain, MCP (`langchain-mcp-adapters`, `FastMCP`), Groq LLMs
- **Frontend:** Jinja2, HTML5, CSS3, Vanilla JavaScript, Marked.js, html2pdf.js
- **Database:** PostgreSQL (`psycopg` + `AsyncPostgresSaver`)
- **External APIs & MCP Tools:** Tavily MCP, AviationStack API, OpenWeather API

## Project Structure

```text
.
├── app.py                          # FastAPI entry point & API routes (/api/travel, /api/travel/approve)
├── backend.py                      # Async LangGraph multi-agent workflow, supervisor, guardrails & HITL
├── mcp_client.py                   # MultiServerMCPClient setup & MCP tool wrappers
├── custom_weather_mcp_server.py    # Custom local FastMCP server for OpenWeather
├── Dockerfile                      # Container configuration for deployment
├── requirements.txt                # Python dependencies
├── static/                         # Static frontend assets (CSS & JS)
├── templates/                      # Jinja2 HTML templates (index.html)
└── tools/                          # Flight and web search tool integrations
```

## Prerequisites

- Python 3.10 or newer
- A running PostgreSQL database (local or cloud such as Neon/Supabase)
- API keys for:
  - **Groq**
  - **Tavily**
  - **AviationStack**
  - **OpenWeather**

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
DATABASE_URL=postgresql://user:password@host:5432/travel_db?sslmode=require
GROQ_API_KEY=your_groq_api_key
AVIATION_STACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
DEFAULT_ORIGIN_IATA=DEL
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the App

Start the FastAPI server:

```bash
python app.py
```

Open your browser at:

```text
http://127.0.0.1:8001
```

## API Endpoints

- `GET /` — Interactive web interface
- `GET /health` — Service health and enabled features check
- `POST /api/travel` — Start a travel-planning workflow and generate a draft itinerary for review
- `POST /api/travel/approve` — Approve the draft or submit feedback to generate the final travel plan

### Example Request

```bash
curl -X POST http://127.0.0 \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 4-day budget trip from Delhi to Manali with hotels and weather forecast"}'
```

## How the Workflow Works

1. **Input & Guardrails**: The user submits a request via the web UI or `POST /api/travel`. The **Supervisor Agent** validates travel intent, extracts constraints, and selects the required specialist agents.
2. **Specialist Research**: Selected agents (**Flight**, **Hotel**, **Weather**, and **Budget**) gather data via MCP servers and LLM analysis.
3. **Draft & Human-in-the-Loop Pause**: The **Itinerary Agent** builds a draft plan, and LangGraph pauses at the `human_approval` node.
4. **Review & Finalize**: Through `POST /api/travel/approve`, the user either approves the draft or provides feedback. The **Final Agent** then generates a 7-section Markdown travel report ready to copy or export as a PDF.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
