# Goal-Based Agent
# Goal: deliver the order before the deadline.
# It predicts the result of each route and takes one that reaches the goal.
# It does NOT care which one is "best", any route that reaches the goal is ok.

from environment import Decision, travel_time


class GoalBasedAgent:
    name = "Goal-Based"

    def goal_reached(self, arrival, s):
        return arrival <= s.deadline

    def decide(self, s):
        d = Decision(self.name)
        d.log.append(f"GOAL: deliver {s.order_id} within {s.deadline} min")

        # try routes from shortest to longest, stop at the first one that works
        chosen = None
        for r in sorted(s.routes, key=lambda r: r.distance):
            arrival = s.prep_time + travel_time(r, s.weather)
            ok = self.goal_reached(arrival, s)
            d.log.append(f"  predict {r.name}: arrive in {arrival:.1f} min -> "
                         f"{'goal met' if ok else 'goal NOT met'}")
            if ok:
                chosen = r
                break

        d.actions.append("Accept order " + s.order_id)
        if chosen is None:
            # no route reaches the goal, get as close as possible and tell the customer
            chosen = min(s.routes, key=lambda r: travel_time(r, s.weather))
            d.log.append("No route meets the goal -> take fastest and inform customer")
            d.actions.append("Notify customer about possible delay")
        else:
            d.log.append(f"Selected {chosen.name} because it achieves the goal")

        d.actions.append("Pick up food")
        d.actions.append("Ride via " + chosen.name)
        d.actions.append("Deliver order")

        d.route = chosen.name
        d.eta = round(s.prep_time + travel_time(chosen, s.weather), 1)
        return d
