# Utility-Based Agent
# Gives every route a score using time, distance, traffic and cost,
# then picks the highest score.

from environment import Decision, travel_time, fuel_cost

TRAFFIC_PENALTY = {"light": 0, "normal": 1, "heavy": 3}


class UtilityBasedAgent:
    name = "Utility-Based"

    def __init__(self):
        # how much each factor matters (weights add up to 1)
        self.weights = {"time": 0.45, "distance": 0.15, "traffic": 0.2, "cost": 0.2}

    def utility(self, r, s, w):
        t = s.prep_time + travel_time(r, s.weather)
        # turn everything into 0..1 where 1 is good
        time_score = max(0, 1 - t / (s.deadline * 1.5))
        dist_score = max(0, 1 - r.distance / 10)
        traffic_score = 1 - TRAFFIC_PENALTY[r.traffic] / 3
        cost_score = max(0, 1 - fuel_cost(r) / 200)
        u = (w["time"] * time_score + w["distance"] * dist_score
             + w["traffic"] * traffic_score + w["cost"] * cost_score)
        # being late is really bad for the company
        if t > s.deadline:
            u -= 0.3
        return round(u, 3), t

    def decide(self, s):
        d = Decision(self.name)
        w = dict(self.weights)
        if s.urgent:
            # urgent order -> time matters a lot more than money
            w = {"time": 0.65, "distance": 0.1, "traffic": 0.15, "cost": 0.1}
            d.log.append("Urgent order -> weights shifted towards time")
        d.log.append(f"weights: {w}")

        best, best_u, best_t = None, -999, None
        for r in s.routes:
            u, t = self.utility(r, s, w)
            d.log.append(f"  {r.name}: time={t:.1f}m dist={r.distance}km "
                         f"traffic={r.traffic} cost=Rs{fuel_cost(r)} -> U={u}")
            if u > best_u:
                best, best_u, best_t = r, u, t

        d.log.append(f"Best utility: {best.name} (U={best_u})")
        d.actions += ["Accept order " + s.order_id, "Pick up food",
                      "Ride via " + best.name, "Deliver order"]
        d.route = best.name
        d.eta = round(best_t, 1)
        return d
