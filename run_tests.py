# Runs all 7 agents on the 3 test cases from the assignment and prints
# the full reasoning + a summary table. Output is also saved to results.txt
#
#   python run_tests.py

from agents import all_agents
from environment import TEST_CASES, travel_time


def describe(s):
    lines = [s.title, "-" * len(s.title)]
    lines.append(f"Order {s.order_id}: {s.food} | prep {s.prep_time}m | deadline {s.deadline}m "
                 f"| weather {s.weather} | urgent {s.urgent} | {s.time_of_day}")
    for r in s.routes:
        extra = []
        if r.toll:
            extra.append(f"toll Rs{r.toll}")
        if r.flood_prone:
            extra.append("flood prone")
        lines.append(f"   {r.name}: {r.distance} km, {r.traffic} traffic, "
                     f"~{travel_time(r, s.weather)} min {', '.join(extra)}")
    return lines


def format_decision(d, s):
    out = [f">> {d.agent} Agent"]
    out += ["   " + l for l in d.log]
    out.append("   Actions: " + " | ".join(d.actions))
    status = "ON TIME" if d.eta is not None and d.eta <= s.deadline else "LATE"
    out.append(f"   Route: {d.route}   ETA: {d.eta} min   ({status})")
    return out


def run(agents=None):
    agents = agents or all_agents()
    lines = []
    summary = []
    for make_case in TEST_CASES:
        s = make_case()
        lines += describe(s) + [""]
        for a in agents:
            d = a.decide(s)
            lines += format_decision(d, s) + [""]
            summary.append((s.title.split(":")[0], d.agent, d.route, d.eta, s.deadline))
        lines.append("=" * 70)

    lines.append("")
    lines.append("SUMMARY")
    lines.append(f"{'Case':<8}{'Agent':<20}{'Route':<22}{'ETA':>6}{'Deadline':>10}")
    for case, agent, route, eta, dl in summary:
        lines.append(f"{case:<8}{agent:<20}{route:<22}{eta:>6}{dl:>10}")
    return "\n".join(lines)


if __name__ == "__main__":
    text = run()
    print(text)
    with open("results.txt", "w") as f:
        f.write(text)
