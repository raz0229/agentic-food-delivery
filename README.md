# Smart Food Delivery Agent - Assignment 1 (Agent Based Modeling)

LabaikGroup - Abdullah Zafar (L1F23BSAI0054), Abdurrehman (L1F23BSAI0050), Talha Abid (L1F23BSAI0058)

Seven single-agent architectures solving the same food delivery problem.

```
environment.py          routes, situations, travel time, the 3 test cases
agents/
  simple_reflex.py      IF-THEN rules only
  model_based.py        keeps internal state (route, traffic, weather, order status)
  goal_based.py         picks a route that meets the deadline
  utility_based.py      scores routes on time / distance / traffic / cost
  learning.py           learns min-per-km from feedback after each trip
  hierarchical.py       accept -> choose route -> pick up -> deliver -> confirm
  contextual.py         uses rush hour, rain, food type, customer note, road conditions
run_tests.py            runs all agents on the 3 cases, writes results.txt
gui.py                  small tkinter GUI
diagrams/               architecture diagrams (+ script to regenerate them)
```

## Running

Only standard library is needed (tkinter comes with python).

```
python run_tests.py
python gui.py
```

To regenerate the diagrams you need graphviz installed:

```
cd diagrams
python make_diagrams.py
```
