# Model-Based Reflex Agent
# Keeps an internal state (current route, traffic it has seen, weather,
# order status) and uses that state together with the rules.
# The state survives between calls, so it remembers what it saw before.

from environment import Decision, travel_time


class ModelBasedReflexAgent:
    name = "Model-Based Reflex"

    def __init__(self):
        self.state = {
            "current_route": None,
            "known_traffic": {},     # route name -> last traffic seen
            "weather": None,
            "order_status": "none",
        }

    def update_state(self, s):
        st = self.state
        st["weather"] = s.weather
        st["order_status"] = "accepted"
        for r in s.routes:
            old = st["known_traffic"].get(r.name)
            # if a road was heavy last time and is heavy again, mark it as a jam spot
            if old == "heavy" and r.traffic == "heavy":
                st["known_traffic"][r.name] = "jam"
            else:
                st["known_traffic"][r.name] = r.traffic

    def decide(self, s):
        d = Decision(self.name)
        self.update_state(s)
        st = self.state
        d.log.append(f"STATE: weather={st['weather']}, status={st['order_status']}, "
                     f"last route={st['current_route']}")
        d.log.append(f"STATE: traffic model = {st['known_traffic']}")

        bad = ("heavy", "jam")
        # roads we believe are OK right now
        ok_routes = [r for r in s.routes if st["known_traffic"][r.name] not in bad]

        # in the rain the model treats normal traffic as almost as bad as heavy
        if st["weather"] == "rain":
            light = [r for r in ok_routes if st["known_traffic"][r.name] == "light"]
            if light:
                ok_routes = light
                d.log.append("RULE: rain in state -> only keep light-traffic roads")

        # prefer staying on the route we were already using (less confusion)
        route = None
        for r in ok_routes:
            if r.name == st["current_route"]:
                route = r
                d.log.append(f"RULE: {r.name} still fine -> keep current route")
                break
        if route is None:
            route = ok_routes[0] if ok_routes else s.routes[0]
            d.log.append(f"RULE: choose {route.name} (first road not jammed in model)")

        st["current_route"] = route.name

        d.actions.append("Accept order " + s.order_id)
        st["order_status"] = "picked_up"
        d.actions.append("Pick up food (status: picked_up)")
        if st["weather"] == "rain":
            d.actions.append("Cover food bag, ride slowly")
        d.actions.append("Ride via " + route.name)
        st["order_status"] = "delivered"
        d.actions.append("Deliver (status: delivered)")

        d.route = route.name
        d.eta = round(s.prep_time + travel_time(route, s.weather), 1)
        return d
