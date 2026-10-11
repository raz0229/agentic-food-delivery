# environment.py
# The delivery "world" that every agent sees. All seven agents get the
# exact same Situation object so we can compare them fairly.

import random
from dataclasses import dataclass, field


# average bike speed in km/h for each traffic level
SPEED = {"light": 30, "normal": 22, "heavy": 10}

# rain slows everyone down a bit
WEATHER_FACTOR = {"clear": 1.0, "cloudy": 1.0, "rain": 0.75}


@dataclass
class Route:
    name: str
    distance: float          # km
    traffic: str             # light / normal / heavy
    toll: int = 0            # rupees
    flood_prone: bool = False


@dataclass
class Situation:
    title: str
    order_id: str
    food: str
    prep_time: int           # minutes the restaurant needs
    deadline: int            # minutes from now the customer expects the food
    weather: str
    urgent: bool
    routes: list
    time_of_day: str = "afternoon"
    customer_note: str = ""
    food_type: str = "hot"   # hot / cold / packed
    vehicle: str = "bike"


@dataclass
class Decision:
    agent: str
    route: str = None
    eta: float = None        # predicted minutes until the customer gets the food
    actions: list = field(default_factory=list)
    log: list = field(default_factory=list)


def travel_time(route, weather):
    """Rough travel time in minutes for a route."""
    speed = SPEED[route.traffic] * WEATHER_FACTOR.get(weather, 1.0)
    return round(route.distance / speed * 60, 1)


def fuel_cost(route):
    # about 12 rupees per km for the bike + toll if any
    return round(route.distance * 12 + route.toll)


def simulate_trip(route, weather, rng=None):
    """What actually happens on the road. Used to give feedback to the
    learning agent. Real trips are never exactly like the estimate."""
    rng = rng or random
    t = travel_time(route, weather)
    # heavy traffic is way more unpredictable than light traffic
    spread = {"light": 0.1, "normal": 0.2, "heavy": 0.45}[route.traffic]
    t = t * rng.uniform(1.0, 1.0 + spread)
    if weather == "rain" and route.flood_prone:
        t += rng.uniform(5, 12)   # water on the road, had to go slow / wait
    return round(t, 1)


# ---------------- the three test cases from the assignment ----------------

def case_1():
    return Situation(
        title="Case 1: Normal traffic, good weather",
        order_id="ORD-101",
        food="2x Zinger burger, 1x fries",
        prep_time=10,
        deadline=40,
        weather="clear",
        urgent=False,
        time_of_day="afternoon",
        customer_note="Leave at the gate",
        food_type="hot",
        routes=[
            Route("Route A (Main Blvd)", 4.0, "normal"),
            Route("Route B (Canal Rd)", 6.0, "light"),
        ],
    )


def case_2():
    return Situation(
        title="Case 2: Heavy traffic, multiple routes",
        order_id="ORD-102",
        food="Large pizza, 1.5L drink",
        prep_time=15,
        deadline=40,
        weather="cloudy",
        urgent=False,
        time_of_day="evening rush",
        customer_note="",
        food_type="hot",
        routes=[
            Route("Route A (Main Blvd)", 4.0, "heavy"),
            Route("Route B (Canal Rd)", 6.5, "light"),
            Route("Route C (Ring Rd)", 5.0, "normal", toll=60),
        ],
    )


def case_3():
    return Situation(
        title="Case 3: Heavy traffic, rain, urgent",
        order_id="ORD-103",
        food="Biryani + ice cream",
        prep_time=8,
        deadline=30,
        weather="rain",
        urgent=True,
        time_of_day="evening rush",
        customer_note="Call on arrival, patient at home",
        food_type="cold",
        routes=[
            Route("Route A (Main Blvd)", 4.0, "heavy"),
            Route("Route C (Underpass)", 5.0, "normal", flood_prone=True),
            Route("Route B (Canal Rd)", 6.0, "light"),
        ],
    )


TEST_CASES = [case_1, case_2, case_3]
