# Hierarchical Agent
# Top goal "deliver order" is broken into sub-tasks. Each sub-task is
# handled by its own small method (lower level of the hierarchy).

from environment import Decision, travel_time


class HierarchicalAgent:
    name = "Hierarchical"

    def decide(self, s):
        d = Decision(self.name)
        d.log.append("TOP GOAL: Deliver order " + s.order_id)
        clock = 0.0

        # subtasks run one after another, each one can stop the plan
        ok, msg = self.accept_order(s)
        d.log.append("  [1] accept_order: " + msg)
        d.actions.append(f"t={clock:.0f}m  Accept order")
        if not ok:
            d.actions.append("Order rejected")
            return d

        route, msg = self.choose_route(s)
        d.log.append("  [2] choose_route: " + msg)
        d.actions.append(f"t={clock:.0f}m  Plan route -> {route.name}")

        clock += s.prep_time
        d.log.append(f"  [3] pick_up_food: wait {s.prep_time} min at restaurant")
        d.actions.append(f"t={clock:.0f}m  Pick up food")

        trip = travel_time(route, s.weather)
        clock += trip
        steps = self.deliver_order(s, route)
        d.log.append("  [4] deliver_order: " + ", ".join(steps))
        d.actions.append(f"t={clock:.0f}m  Deliver order")

        msg = self.confirm_delivery(s, clock)
        d.log.append("  [5] confirm_delivery: " + msg)
        d.actions.append(f"t={clock:.0f}m  Confirm delivery")

        d.route = route.name
        d.eta = round(clock, 1)
        return d

    # ---- sub-tasks ----

    def accept_order(self, s):
        fastest = min(travel_time(r, s.weather) for r in s.routes)
        if s.prep_time + fastest > s.deadline * 1.5:
            return False, "impossible to deliver even close to time"
        return True, "order accepted"

    def choose_route(self, s):
        # lower-level policy: fastest route that is on time, cheaper one on ties
        options = sorted(s.routes, key=lambda r: (travel_time(r, s.weather), r.toll))
        best = options[0]
        return best, f"{best.name} ({travel_time(best, s.weather)} min ride)"

    def deliver_order(self, s, route):
        steps = ["leave restaurant"]
        if s.weather == "rain":
            steps.append("put on rain cover")
        steps.append("follow " + route.name.split(" (")[0])
        if s.urgent:
            steps.append("no stops (urgent)")
        steps.append("reach customer")
        return steps

    def confirm_delivery(self, s, clock):
        if clock <= s.deadline:
            return f"on time ({clock:.1f}/{s.deadline} min), ask for rating"
        return f"LATE by {clock - s.deadline:.1f} min, apologise + voucher"
