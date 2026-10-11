# Generates one architecture diagram per agent using graphviz (dot).
# Needs graphviz installed:  sudo pacman -S graphviz / apt install graphviz
#
#   python make_diagrams.py

import subprocess

BASE = """digraph G {
  rankdir=LR;
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, fillcolor="#e8f0fe"];
  edge [fontname="Helvetica", fontsize=9];
  label="%s"; labelloc=t; fontsize=16; fontname="Helvetica-Bold";
  env [label="Environment\\n(orders, routes,\\ntraffic, weather)", shape=ellipse, fillcolor="#e6f4ea"];
  per [label="Input / Perception\\n(sensors)"];
  act [label="Action\\n(route + delivery steps)", fillcolor="#fde7e7"];
  env -> per [label="percepts"];
  act -> env [label="acts on"];
%s
}
"""

DIAGRAMS = {
    "simple_reflex": ("Simple Reflex Agent", """
  rules [label="Condition-Action Rules\\nIF heavy traffic -> alt route\\nIF rain -> ride slow\\nIF urgent -> priority", fillcolor="#fff4d6"];
  dec [label="Decision Process\\n(match current percept\\nto a rule)"];
  per -> dec; rules -> dec; dec -> act;
"""),
    "model_based": ("Model-Based Reflex Agent", """
  state [label="Internal State\\ncurrent route, traffic seen,\\nweather, order status", fillcolor="#fff4d6"];
  model [label="Model of world\\n(how traffic/rain\\naffect roads)", fillcolor="#fff4d6"];
  rules [label="Condition-Action\\nRules", fillcolor="#fff4d6"];
  dec [label="Decision Process"];
  per -> state [label="update"]; model -> state; state -> dec; rules -> dec; dec -> act;
  act -> state [label="what my action did", style=dashed];
"""),
    "goal_based": ("Goal-Based Agent", """
  state [label="State\\n(routes, prep time)", fillcolor="#fff4d6"];
  pred [label="Prediction\\nWhat happens if I take\\nroute X? (arrival time)"];
  goal [label="Goal\\nDeliver before deadline", fillcolor="#fff4d6"];
  dec [label="Decision Process\\n(pick a route that\\nachieves the goal)"];
  per -> state -> pred -> dec; goal -> dec; dec -> act;
"""),
    "utility_based": ("Utility-Based Agent", """
  state [label="State\\n(all candidate routes)", fillcolor="#fff4d6"];
  pred [label="Prediction\\ntime, distance,\\ntraffic, cost per route"];
  util [label="Utility Function\\nU = w1*time + w2*dist\\n+ w3*traffic + w4*cost", fillcolor="#fff4d6"];
  dec [label="Decision Process\\n(choose max utility)"];
  per -> state -> pred -> util -> dec -> act;
"""),
    "learning": ("Learning Agent", """
  critic [label="Critic\\n(expected vs actual\\ndelivery time)", fillcolor="#fff4d6"];
  learn [label="Learning Element\\n(update min/km\\nestimates)", fillcolor="#fff4d6"];
  know [label="Knowledge\\npast deliveries", fillcolor="#fff4d6"];
  perf [label="Performance Element\\n(pick route with lowest\\nexpected time)"];
  prob [label="Problem Generator\\n(explore other routes)", fillcolor="#fff4d6"];
  per -> perf; know -> perf; perf -> act;
  per -> critic [label="feedback"]; critic -> learn; learn -> know [label="update"];
  prob -> perf [style=dashed];
"""),
    "hierarchical": ("Hierarchical Agent", """
  top [label="Top Goal\\nDeliver order", fillcolor="#fff4d6"];
  s1 [label="1. Accept order"]; s2 [label="2. Choose route"]; s3 [label="3. Pick up food"];
  s4 [label="4. Deliver order"]; s5 [label="5. Confirm delivery"];
  per -> top; top -> s1 -> s2 -> s3 -> s4 -> s5; s5 -> act;
  {rank=same; s1; s2; s3; s4; s5;}
"""),
    "contextual": ("Contextual Agent", """
  ctx [label="Context Collector\\ntime of day, weather, food type,\\ncustomer note, road conditions,\\nurgency", fillcolor="#fff4d6"];
  adapt [label="Context Rules\\n(avoid flood roads in rain,\\nrush hour buffer,\\nbag type, toll vs time)", fillcolor="#fff4d6"];
  dec [label="Decision Process\\n(route + handling\\nadapted to context)"];
  per -> ctx -> adapt -> dec -> act;
"""),
}

if __name__ == "__main__":
    for name, (title, body) in DIAGRAMS.items():
        dot = BASE % (title, body)
        subprocess.run(["dot", "-Tpng", "-Gdpi=130", "-o", name + ".png"],
                       input=dot.encode(), check=True)
        print("made", name + ".png")
