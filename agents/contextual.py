# Contextual Agent
# First collects the context around the delivery (time of day, weather,
# food type, customer note, road conditions, urgency) and then lets that
# context change both the route choice and the way the order is handled.

from environment import Decision, travel_time


class ContextualAgent:
    name = "Contextual"

    def collect_context(self, s):
        return {
            "rush_hour": "rush" in s.time_of_day,
            "raining": s.weather == "rain",
            "urgent": s.urgent,
            "food_type": s.food_type,
            "note": s.customer_note,
            "vehicle": s.vehicle,
        }

    def decide(self, s):
        d = Decision(self.name)
        ctx = self.collect_context(s)
        d.log.append(f"CONTEXT: {ctx}")

        routes = list(s.routes)

        # context 1: rain + flood prone road = risky, drop it
        if ctx["raining"]:
            safe = [r for r in routes if not r.flood_prone]
            for r in routes:
                if r.flood_prone:
                    d.log.append(f"  rain -> avoid {r.name} (floods in rain)")
            routes = safe or routes

        # context 2: rush hour makes traffic worse than reported, add a buffer
        buffer = 1.2 if ctx["rush_hour"] else 1.0
        if ctx["rush_hour"]:
            d.log.append("  rush hour -> add 20% buffer to heavy/normal roads")

        def est(r):
            t = travel_time(r, s.weather)
            return t * buffer if r.traffic != "light" else t

        # context 3: cold/hot food or urgent order -> shortest time wins,
        # otherwise a toll road is not worth a couple of minutes
        if ctx["urgent"] or ctx["food_type"] == "cold":
            route = min(routes, key=est)
            d.log.append("  urgent/cold food -> pick fastest safe road")
        else:
            route = min(routes, key=lambda r: est(r) + r.toll / 20)
            d.log.append("  normal order -> balance time and toll")

        # context also changes how the order is handled
        d.actions.append("Accept order " + s.order_id)
        if ctx["food_type"] == "hot":
            d.actions.append("Use insulated hot bag")
        elif ctx["food_type"] == "cold":
            d.actions.append("Use cooler bag with ice pack")
        d.actions.append("Pick up food")
        if ctx["raining"]:
            d.actions.append("Wear raincoat, waterproof the bag")
        d.actions.append("Ride via " + route.name)
        if ctx["note"]:
            d.actions.append("Customer note: " + ctx["note"])
        d.actions.append("Deliver order")

        d.route = route.name
        d.eta = round(s.prep_time + est(route), 1)
        return d
