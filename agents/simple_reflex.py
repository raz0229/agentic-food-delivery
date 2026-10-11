# Simple Reflex Agent
# Only looks at the current percept and fires IF-THEN rules.
# No memory, no planning, no comparing routes.

from environment import Decision, travel_time


class SimpleReflexAgent:
    name = "Simple Reflex"

    def decide(self, s):
        d = Decision(self.name)
        default = s.routes[0]   # the usual (shortest) route the rider takes

        # Rule 1: IF traffic is heavy THEN take an alternative route
        if default.traffic == "heavy" and len(s.routes) > 1:
            route = s.routes[1]   # just grabs the next one, doesn't compare
            d.log.append(f"RULE: traffic on {default.name} is heavy -> switch to {route.name}")
        else:
            route = default
            d.log.append(f"RULE: traffic is {default.traffic} -> stay on {route.name}")

        d.actions.append("Pick up order " + s.order_id)

        # Rule 2: IF raining THEN ride slowly and cover the food
        if s.weather == "rain":
            d.log.append("RULE: it is raining -> ride slowly, cover food bag")
            d.actions.append("Cover food bag and ride slowly")

        # Rule 3: IF urgent THEN mark as priority
        if s.urgent:
            d.log.append("RULE: order is urgent -> priority delivery")
            d.actions.append("Mark as priority")

        d.actions.append("Ride via " + route.name)
        d.actions.append("Hand over order")

        d.route = route.name
        d.eta = round(s.prep_time + travel_time(route, s.weather), 1)
        return d
