# Learning Agent
# Learns how many minutes per km it really takes under each
# (traffic, weather) condition, from previous deliveries + feedback.
#
#   performance element -> picks route with lowest expected time
#   critic             -> compares expected vs actual time
#   learning element   -> updates the estimate (running average)
#   problem generator  -> sometimes tries another route (exploration)

import random
from environment import Decision, simulate_trip


class LearningAgent:
    name = "Learning"

    def __init__(self, alpha=0.3, explore=0.1, seed=7):
        self.alpha = alpha
        self.explore = explore
        self.rng = random.Random(seed)
        # past delivery experience (minutes per km). Old data was mostly
        # collected at night so heavy traffic looks less bad than it is.
        self.mpk = {
            ("light", "clear"): 2.0, ("normal", "clear"): 2.8, ("heavy", "clear"): 3.5,
            ("light", "rain"): 2.7, ("normal", "rain"): 3.6, ("heavy", "rain"): 4.5,
        }
        self.history = []

    def key(self, r, weather):
        w = "rain" if weather == "rain" else "clear"
        return (r.traffic, w)

    def expected(self, r, weather):
        return r.distance * self.mpk[self.key(r, weather)]

    def decide(self, s, give_feedback=True):
        d = Decision(self.name)
        for r in s.routes:
            d.log.append(f"  learned estimate {r.name}: {self.expected(r, s.weather):.1f} min "
                         f"({self.mpk[self.key(r, s.weather)]:.2f} min/km)")

        route = min(s.routes, key=lambda r: self.expected(r, s.weather))
        # every now and then try something different to keep learning
        if len(s.routes) > 1 and self.rng.random() < self.explore and not s.urgent:
            route = self.rng.choice([r for r in s.routes if r is not route])
            d.log.append(f"Exploring: trying {route.name} this time")
        else:
            d.log.append(f"Best known route: {route.name}")

        expected = self.expected(route, s.weather)
        d.actions += ["Accept order " + s.order_id, "Pick up food",
                      "Ride via " + route.name, "Deliver order"]
        d.route = route.name
        d.eta = round(s.prep_time + expected, 1)

        if give_feedback:
            actual = simulate_trip(route, s.weather, self.rng)
            self.learn(route, s.weather, actual)
            d.log.append(f"FEEDBACK: expected {expected:.1f} min, actual {actual} min")
            d.log.append(f"Updated {self.key(route, s.weather)} -> "
                         f"{self.mpk[self.key(route, s.weather)]:.2f} min/km")
            d.actions.append("Record feedback for next time")
        return d

    def learn(self, route, weather, actual_minutes):
        k = self.key(route, weather)
        observed = actual_minutes / route.distance
        self.mpk[k] += self.alpha * (observed - self.mpk[k])
        self.history.append((route.name, weather, actual_minutes))

    def train(self, situation_makers, episodes=20):
        """Run a bunch of practice deliveries so the agent can learn."""
        for i in range(episodes):
            s = situation_makers[i % len(situation_makers)]()
            self.decide(s)
