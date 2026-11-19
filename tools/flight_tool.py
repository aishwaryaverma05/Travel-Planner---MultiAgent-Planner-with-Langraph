import os
import re
import certifi
import airportsdata
import pycountry
from dotenv import load_dotenv
import requests

load_dotenv()

# Protect against SSL errors
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "JFK")
BASE_URL = "https://api.aviationstack.com/v1/flights"

AIRPORTS = airportsdata.load("IATA")

COUNTRY_ALIASES = {
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "america": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "uae": "United Arab Emirates",
    "u.a.e.": "United Arab Emirates",
    "emirates": "United Arab Emirates",
    "dubai": "United Arab Emirates",  # Helpful fallback if user types city as country
    "aus": "Australia",
    "oz": "Australia",
    "nz": "New Zealand",
    "sa": "South Africa",
    "rsa": "South Africa",
    "holland": "Netherlands",
    "the netherlands": "Netherlands",
    "russia": "Russian Federation",
    "south korea": "Korea, Republic of",
    "korea": "Korea, Republic of",
    "north korea": "Korea, Democratic People's Republic of",
    "vietnam": "Viet Nam",
    "turkey": "Türkiye",
    "turkiye": "Türkiye",
    "czech republic": "Czechia",
    "czech": "Czechia",
    "taiwan": "Taiwan, Province of China",
    "iran": "Iran, Islamic Republic of",
    "syria": "Syrian Arab Republic",
    "venezuela": "Venezuela, Bolivarian Republic of",
    "bolivia": "Bolivia, Plurinational State of",
    "tanzania": "Tanzania, United Republic of",
    "moldova": "Moldova, Republic of",
    "laos": "Lao People's Democratic Republic",
    "brunei": "Brunei Darussalam",
    "ivory coast": "Côte d'Ivoire",
    "cote d'ivoire": "Côte d'Ivoire",
    "cape verde": "Cabo Verde",
    "swaziland": "Eswatini",
    "burma": "Myanmar",
    "macedonia": "North Macedonia",
    "vatican": "Holy See",
    "vatican city": "Holy See",
    "palestine": "Palestine, State of",
    "bharat": "India",
    "hindustan": "India",
    "lanka": "Sri Lanka",
    "ceylon": "Sri Lanka",
    "maldive": "Maldives",
}

COUNTRY_MAIN_AIRPORT = {
    "India": "DEL",
    "Sri Lanka": "CMB",
    "Maldives": "MLE",
    "Nepal": "KTM",
    "Bhutan": "PBH",
    "Bangladesh": "DAC",
    "United Arab Emirates": "DXB",
    "Thailand": "BKK",
    "Singapore": "SIN",
    "Malaysia": "KUL",
    "Indonesia": "DPS",
    "Viet Nam": "SGN",
    "Japan": "HND",
    "Korea, Republic of": "ICN",
    "China": "PEK",
    "Qatar": "DOH",
    "Saudi Arabia": "RUH",
    "Oman": "MCT",
    "United Kingdom": "LHR",
    "France": "CDG",
    "Germany": "FRA",
    "Netherlands": "AMS",
    "Italy": "FCO",
    "Spain": "MAD",
    "Switzerland": "ZRH",
    "Türkiye": "IST",
    "Russian Federation": "SVO",
    "Greece": "ATH",
    "United States": "JFK",
    "Canada": "YYZ",
    "Mexico": "MEX",
    "Australia": "SYD",
    "New Zealand": "AKL",
    "South Africa": "JNB",
    "Egypt": "CAI",
    "Mauritius": "MRU",
}

CITY_MAIN_AIRPORTS = {
    "delhi": "DEL",
    "new delhi": "DEL",
    "mumbai": "BOM",
    "bombay": "BOM",
    "bengaluru": "BLR",
    "bangalore": "BLR",
    "chennai": "MAA",
    "madras": "MAA",
    "kolkata": "CCU",
    "calcutta": "CCU",
    "hyderabad": "HYD",
    "goa": "GOI",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "kochi": "COK",
    "cochin": "COK",
    "lucknow": "LKO",
    "chandigarh": "IXC",
    "guwahati": "GAU",
    "thiruvananthapuram": "TRV",
    "trivandrum": "TRV",
    "varanasi": "VNS",
    "amritsar": "ATQ",
    "srinagar": "SXR",
    "leh": "IXL",
    "udaipur": "UDR",
    "jodhpur": "JDH",
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "sharjah": "SHJ",
    "doha": "DOH",
    "riyadh": "RUH",
    "jeddah": "JED",
    "muscat": "MCT",
    "kuwait city": "KWI",
    "bahrain": "BAH",
    "bangkok": "BKK",
    "phuket": "HKT",
    "krabi": "KBV",
    "chiang mai": "CNX",
    "singapore": "SIN",
    "kuala lumpur": "KUL",
    "bali": "DPS",
    "denpasar": "DPS",
    "jakarta": "CGK",
    "hanoi": "HAN",
    "ho chi minh city": "SGN",
    "saigon": "SGN",
    "da nang": "DAD",
    "tokyo": "HND",
    "osaka": "KIX",
    "kyoto": "KIX",
    "seoul": "ICN",
    "beijing": "PEK",
    "shanghai": "PVG",
    "hong kong": "HKG",
    "taipei": "TPE",
    "colombo": "CMB",
    "male": "MLE",
    "malé": "MLE",
    "kathmandu": "KTM",
    "paro": "PBH",
    "dhaka": "DAC",
    "london": "LHR",
    "manchester": "MAN",
    "edinburgh": "EDI",
    "paris": "CDG",
    "nice": "NCE",
    "frankfurt": "FRA",
    "munich": "MUC",
    "berlin": "BER",
    "amsterdam": "AMS",
    "rome": "FCO",
    "milan": "MXP",
    "venice": "VCE",
    "madrid": "MAD",
    "barcelona": "BCN",
    "zurich": "ZRH",
    "geneva": "GVA",
    "vienna": "VIE",
    "prague": "PRG",
    "athens": "ATH",
    "santorini": "JTR",
    "istanbul": "IST",
    "moscow": "SVO",
    "new york": "JFK",
    "nyc": "JFK",
    "los angeles": "LAX",
    "la": "LAX",
    "san francisco": "SFO",
    "chicago": "ORD",
    "miami": "MIA",
    "las vegas": "LAS",
    "boston": "BOS",
    "washington": "IAD",
    "seattle": "SEA",
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
    "mexico city": "MEX",
    "cancun": "CUN",
    "sydney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",
    "auckland": "AKL",
    "queenstown": "ZQN",
    "johannesburg": "JNB",
    "cape town": "CPT",
    "cairo": "CAI",
    "mauritius": "MRU",
}

def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    stop_words = [
        "flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "hotel",
        "hotels", "sightseeing", "under", "budget", "info", "information"
    ]
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words).strip()



def country_name_to_code(text: str):
    text = clean_text(text)

    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]

    try:
        country = pycountry.countries.lookup(text)
        return country.alpha_2
    except LookupError:
        pass

    # Detect country name inside longer text
    for country in pycountry.countries:
        country_name = country.name.lower()
        if country_name in text:
            return country.alpha_2

    for alias, code in COUNTRY_ALIASES.items():
        if alias in text:
            return code

    return None



def airport_country_matches(airport: dict, country_code: str) -> bool:
    airport_country = str(airport.get("country", "")).upper().strip()

    if airport_country == country_code:
        return True

    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country and airport_country.lower() == country.name.lower():
            return True
    except Exception:
        pass

    return False




def get_best_airport_for_country(country_code: str):
    preferred = COUNTRY_MAIN_AIRPORT.get(country_code)

    if preferred and preferred in AIRPORTS:
        return preferred

    candidates = []

    for iata, airport in AIRPORTS.items():
        if not iata:
            continue

        if airport_country_matches(airport, country_code):
            name = str(airport.get("name", "")).lower()
            city = str(airport.get("city", "")).lower()

            score = 0

            if "international" in name:
                score += 50
            if "intl" in name:
                score += 40
            if "capital" in name:
                score += 20
            if city:
                score += 5

            candidates.append((score, iata))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]




def resolve_location_to_iata(location: str):
    """
    Converts country/city/airport/IATA into IATA code.

    Examples:
    Bangladesh -> DAC
    Japan -> NRT
    Dhaka -> DAC
    Tokyo -> NRT
    DAC -> DAC
    """

    if not location:
        return None

    raw_location = location.strip()

    # Direct IATA code
    if re.fullmatch(r"[A-Za-z]{3}", raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code

    location_clean = clean_text(raw_location)

    if not location_clean:
        return None

    # City preferred airport
    if location_clean in CITY_MAIN_AIRPORTS:
        return CITY_MAIN_AIRPORTS[location_clean]

    # Country preferred airport
    country_code = country_name_to_code(location_clean)
    if country_code:
        airport = get_best_airport_for_country(country_code)
        if airport:
            return airport

    # Exact city match from airport database
    city_matches = []

    for iata, airport in AIRPORTS.items():
        city = str(airport.get("city", "")).lower().strip()
        name = str(airport.get("name", "")).lower().strip()

        score = 0

        if city == location_clean:
            score += 100
        elif location_clean in city:
            score += 70

        if location_clean in name:
            score += 50

        if "international" in name:
            score += 10

        if score > 0:
            city_matches.append((score, iata))

    if city_matches:
        city_matches.sort(reverse=True)
        return city_matches[0][1]

    return None




def find_location_mentions(query: str):
    """
    Finds country or city names inside a natural language query.
    """

    q = query.lower()
    mentions = []

    # Country aliases
    for alias in COUNTRY_ALIASES:
        if re.search(rf"\b{re.escape(alias)}\b", q):
            mentions.append(alias)

    # Country names from pycountry
    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4 and re.search(rf"\b{re.escape(name)}\b", q):
            mentions.append(name)

    # City names from our preferred city map
    for city in CITY_MAIN_AIRPORT:
        if re.search(rf"\b{re.escape(city)}\b", q):
            mentions.append(city)

    # Remove duplicate while keeping order
    unique_mentions = []
    for item in mentions:
        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions


def parse_route(query: str):
    """
    Returns:
    dep_iata, arr_iata

    Can return:
    None, None  -> global live flights
    DAC, NRT    -> filtered route
    DAC, None   -> all flights from DAC
    None, NRT   -> all flights to NRT
    """

    q = query.strip()
    q_lower = q.lower()

    # Global / all-country query
    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]

    if any(keyword in q_lower for keyword in global_keywords):
        return None, None

    # Direct IATA code route: DAC to NRT
    codes = re.findall(r"\b[A-Z]{3}\b", q)

    if len(codes) >= 2:
        dep = codes[0].upper()
        arr = codes[1].upper()
        return dep, arr

    # Pattern: from X to Y
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        origin_text = match.group(1)
        dest_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: to Y from X
    match = re.search(
        r"\bto\s+(.+?)\s+\bfrom\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        dest_text = match.group(1)
        origin_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: flights from X
    match = re.search(r"\bfrom\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        origin_text = match.group(1)
        dep_iata = resolve_location_to_iata(origin_text)
        return dep_iata, None

    # Pattern: flights to X
    match = re.search(r"\bto\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        dest_text = match.group(1)
        arr_iata = resolve_location_to_iata(dest_text)
        return None, arr_iata

    # Fallback: find country/city mentions
    mentions = find_location_mentions(q)

    if len(mentions) >= 2:
        dep_iata = resolve_location_to_iata(mentions[0])
        arr_iata = resolve_location_to_iata(mentions[1])
        return dep_iata, arr_iata

    if len(mentions) == 1:
        arr_iata = resolve_location_to_iata(mentions[0])
        return DEFAULT_ORIGIN_IATA, arr_iata

    return None, None


def format_flight(flight: dict):
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep = flight.get("departure", {}) or {}
    arr = flight.get("arrival", {}) or {}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata = dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate = dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate = arr.get("gate") or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()


def search_flights(query: str, limit: int = 10):
    if not API_KEY:
        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add this in your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )

    dep_iata, arr_iata = parse_route(query)

    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Flight API request failed: {e}"
    except ValueError:
        return "Flight API returned invalid JSON."

    if "error" in data:
        error = data["error"]
        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )

    flight_data = data.get("data", [])

    if not flight_data:
        route_text = ""

        if dep_iata and arr_iata:
            route_text = f" for route {dep_iata} to {arr_iata}"
        elif dep_iata:
            route_text = f" from {dep_iata}"
        elif arr_iata:
            route_text = f" to {arr_iata}"

        return (
            f"No live flight data found{route_text}.\n\n"
            "Note: AviationStack provides live/status flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing API such as Amadeus."
        )

    route_info = "Global live flights"

    if dep_iata and arr_iata:
        route_info = f"Live flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info = f"Live flights from {dep_iata}"
    elif arr_iata:
        route_info = f"Live flights to {arr_iata}"

    formatted_flights = [format_flight(flight) for flight in flight_data[:limit]]

    return f"{route_info}\n\n" + "\n\n---\n\n".join(formatted_flights)


if __name__ == "__main__":
    print(search_flights("Plan a 7 days Japan trip from Bangladesh"))
    print("\n" + "=" * 80 + "\n")
    print(search_flights("all country flight info"))