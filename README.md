# PlanMyTrip - MultiAgent Travel Planner

An open-source AI travel planner that turns a natural-language trip request into a practical travel plan with flight suggestions, hotel ideas, live weather forecasts, and a day-by-day itinerary. The project uses a multi-agent workflow built with **LangGraph**, **LangChain**, **Model Context Protocol (MCP)**, and **FastAPI**.

## Why this project?

Planning a trip usually means jumping between multiple websites, tools, and spreadsheets. This project brings that flow into one experience by combining:

- a flight-search agent,
- a hotel-research agent,
- a weather-forecast agent (powered by a custom FastMCP server),
- an itinerary-planning agent, and
- a final response agent,

all coordinated through an asynchronous LangGraph workflow.

## Features

- **Multi-Agent Orchestration** with LangGraph
- **MCP Integration (`MultiServerMCPClient`)** connecting remote and local MCP servers
- **Custom Weather MCP Server (`FastMCP`)** for real-time weather and short-term forecasts via OpenWeather
- **Flight Research** using AviationStack
- **Hotel & Destination Suggestions** using Tavily MCP search
- **FastAPI Backend** with async lifespan management and an interactive HTML/CSS/JS frontend
- **PDF Export & One-Click Copy** for generated travel plans
- **Conversation State Persistence** using PostgreSQL
- **Fast LLM Inference** powered by Groq

## Tech Stack

- **Backend & AI:** Python 3.10+, FastAPI, LangGraph, LangChain, MCP (`langchain-mcp-adapters`, `FastMCP`), Groq LLMs
- **Frontend:** Jinja2, HTML5, CSS3, Vanilla JavaScript, Marked.js, html2pdf.js
- **Database:** PostgreSQL
- **External APIs & MCP Tools:** Tavily MCP, AviationStack API, OpenWeather API

## Project Structure

```text
.
├── app.py                          # FastAPI app entry point & async lifespan
├── backend.py                      # LangGraph multi-agent travel workflow
├── mcp_client.py                   # MultiServerMCPClient setup & tool wrappers
├── custom_weather_mcp_server.py    # Custom local FastMCP server for OpenWeather
├── requirements.txt                # Python dependencies
├── static/                         # Static frontend assets (CSS & JS)
├── templates/                      # Jinja2 HTML templates
└── tools/                          # Flight and web search tool integrations
```

## Prerequisites

Before running the project locally, make sure you have:

- Python 3.10 or newer installed
- PostgreSQL running and accessible
- API keys for:
  - **Groq**
  - **Tavily**
  - **AviationStack**
  - **OpenWeather**

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db
GROQ_API_KEY=your_groq_api_key
AVIATION_STACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
DEFAULT_ORIGIN_IATA=DAC
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

Then open your browser at:

```text
http://127.0.0
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/travel` - Submit a travel request

Example request:

```bash
curl -X POST http://127.0.0api/travel \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 3-day trip to Tokyo with flights, hotels, and weather forecast"}'
```

## How the Workflow Works

1. The user submits a natural-language travel request via the web UI or `/api/travel` endpoint.
2. FastAPI passes the request to the asynchronous LangGraph multi-agent pipeline.
3. Specialized agents query **AviationStack**, **Tavily MCP**, and the local **FastMCP Weather Server** in parallel.
4. The itinerary and final response agents synthesize the gathered data into a structured, budget-aware Markdown report.
5. The frontend renders the formatted plan with options to copy or download as a PDF.

## Contributing

Contributions are welcome. If you want to improve the app, add new travel features, or fix issues:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Open a pull request

## Acknowledgments

This project is built with modern LLM, LangGraph, and MCP tooling, and is intended as a practical example of combining multi-agent systems with custom and remote MCP servers.
