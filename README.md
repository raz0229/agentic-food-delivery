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

## Test cases

All agents get the exact same input for each case.

| Case | Situation | Prep / Deadline | Routes (ride time) |
|---|---|---|---|
| 1 | Normal traffic, clear weather, not urgent, afternoon | 10 / 40 min | A: Main Blvd 4 km normal (10.9 min)<br>B: Canal Rd 6 km light (12.0 min) |
| 2 | Heavy traffic, multiple routes, cloudy, evening rush | 15 / 40 min | A: Main Blvd 4 km **heavy** (24.0 min)<br>B: Canal Rd 6.5 km light (13.0 min)<br>C: Ring Rd 5 km normal, Rs 60 toll (13.6 min) |
| 3 | Heavy traffic, **rain**, **urgent** (ice cream, patient at home), evening rush | 8 / 30 min | A: Main Blvd 4 km **heavy** (32.0 min)<br>C: Underpass 5 km normal, **floods in rain** (18.2 min)<br>B: Canal Rd 6 km light (16.0 min) |

Speeds used: light 30 km/h, normal 22 km/h, heavy 10 km/h, and everything is x0.75 in rain.

## Results

ETA = prep time + ride time (minutes until the customer gets the food).

| Agent | Case 1 | Case 2 | Case 3 |
|---|---|---|---|
| Simple Reflex | A (Main Blvd) - 20.9 | B (Canal Rd) - 28.0 | **C (Underpass) - 26.2** |
| Model-Based Reflex | A (Main Blvd) - 20.9 | B (Canal Rd) - 28.0 | B (Canal Rd) - 24.0 |
| Goal-Based | A (Main Blvd) - 20.9 | **A (Main Blvd) - 39.0** | **C (Underpass) - 26.2** |
| Utility-Based | **B (Canal Rd) - 22.0** | B (Canal Rd) - 28.0 | B (Canal Rd) - 24.0 |
| Learning | A (Main Blvd) - 21.2 | B (Canal Rd) - 28.0 | B (Canal Rd) - 24.2 |
| Hierarchical | A (Main Blvd) - 20.9 | B (Canal Rd) - 28.0 | B (Canal Rd) - 24.0 |
| Contextual | A (Main Blvd) - 20.9 | B (Canal Rd) - 28.0 | B (Canal Rd) - 24.0 |

Bold = the agent did something different from the rest. Every ETA is inside the deadline,
but the underpass in case 3 floods in rain. In the simulation that adds 5-12 min, so
it can easily go past the 30 min deadline.

### Case 1 - normal traffic, good weather

Easy case, so almost everyone picks the shorter Main Blvd.

- **Utility-Based** is the only one that picks Canal Rd. The scores are very close
  (A: U=0.669, B: U=0.673). Canal Rd has light traffic, which made up for it being 1 min slower and costing Rs 24 more.
- **Learning** expected 11.2 min on Main Blvd (2.80 min/km from past data) and the actual trip was 11.2 min.
- **Hierarchical** gives a timeline: accept at t=0, pick up at t=10, deliver at t=21, confirm on time.
- **Contextual** sees hot food plus a customer note, so it adds "use insulated hot bag" and "leave at the gate".

### Case 2 - heavy traffic, multiple routes

- **Simple Reflex** fires `IF traffic heavy -> alternative route` and takes the next route
  in the list (Canal Rd). That worked out here, but only by luck of the list order.
- **Goal-Based** checks routes from shortest to longest. Main Blvd arrives at 39.0 min, which
  is <= 40, so the goal is met and it stops there. It's on time, but with only 1 min to spare
  on a jammed road.
- **Utility-Based** scores: A = 0.400 (heavy + slow), B = 0.615, C = 0.524 (toll makes it expensive) -> picks B.
- **Model-Based** remembers its last route (Main Blvd from case 1) but the model now says it's heavy, so it moves to Canal Rd.
- **Contextual** notices the evening rush and adds a 20% buffer to the heavy and normal roads, and it also weighs the toll -> Canal Rd.

### Case 3 - heavy traffic, rain, urgent

The case where the architectures really split.

- **Simple Reflex**: Main Blvd is heavy, so it takes the next route = the **flood-prone underpass**. It
  also fires the rain rule (ride slow, cover bag) and the urgent rule (priority).
- **Goal-Based**: Main Blvd = 40.0 min (goal NOT met), Underpass = 26.2 min (goal met), so it takes the
  **underpass**. It doesn't know about the flooding risk and doesn't look any further.
- **Model-Based**: the state has Main Blvd as `jam` (heavy twice in a row), and the rain rule keeps only
  light roads, so it stays on Canal Rd (its current route).
- **Utility-Based**: urgent, so the weights shift to time (0.65). A = -0.092 (late penalty), C = 0.492, B = 0.557 -> Canal Rd.
- **Learning**: estimates from experience are A 18.0, C 18.0, B 16.2 min -> Canal Rd. Actual was 16.6 min, so the estimate is updated.
- **Hierarchical**: accept -> choose route (Canal Rd, 16 min) -> pick up at t=8 -> deliver with rain cover
  and no stops -> confirm on time at 24/30 min.
- **Contextual**: drops the underpass because of the rain, adds the rush hour buffer, then picks the fastest safe road
  because the food is cold. It also uses a cooler bag with an ice pack, wears a raincoat, and follows the note "call on arrival".

### Learning agent after training

A fresh learning agent trained for 20 deliveries (GUI button "Train learner", or `LearningAgent().train(TEST_CASES, 20)`).
The starting data was mostly collected at night, so it thought heavy traffic was not that bad:

| Condition (traffic, weather) | min/km before | min/km after 20 trips |
|---|---|---|
| light, clear | 2.00 | 2.06 |
| normal, clear | 2.80 | 3.02 |
| heavy, clear | 3.50 | **5.34** |
| light, rain | 2.70 | 2.79 |
| normal, rain | 3.60 | 3.60 (never tried) |
| heavy, rain | 4.50 | 4.50 (never tried) |

The heavy traffic estimate went up a lot once it actually drove (explored) on heavy roads.
It never explores on urgent orders, which is why the rain values for heavy and normal roads didn't change.

## Comparison

| Agent | Uses | Good | Bad |
|---|---|---|---|
| Simple Reflex | current percept + rules | simple, fast | can't compare routes, took the flooding road |
| Model-Based Reflex | internal state | remembers jams, weather, order status | still rule based, doesn't optimise |
| Goal-Based | predicted arrival vs deadline | always tries to be on time | happy with *any* route that meets the goal (39/40 min in case 2) |
| Utility-Based | time, distance, traffic, cost | best trade-offs, adapts weights for urgent orders | depends on hand picked weights, didn't know about flooding |
| Learning | past deliveries + feedback | estimates get better over time | can be wrong early, exploring sometimes picks worse routes |
| Hierarchical | subgoals | clear step-by-step plan, easy to extend | route choice itself is basic (just fastest) |
| Contextual | rush hour, rain, food, note, road condition | most realistic decisions and handling | needs a lot of context information |

## Conclusion

The **Contextual agent** was the most suitable for this scenario, and the **Utility-Based agent** was a close second.
Food delivery depends a lot on context (rain, rush hour, flooded roads, hot/cold food, customer notes), and the
contextual agent was the only one that used all of it. It picked the fastest *safe* route in every case and also
changed how the order was handled. A real system would ideally combine them: hierarchical steps for the delivery, a
contextual + utility decision for the route, and learning to keep improving the time estimates.

<details>
<summary>Full output of run_tests.py</summary>

```
Case 1: Normal traffic, good weather
------------------------------------
Order ORD-101: 2x Zinger burger, 1x fries | prep 10m | deadline 40m | weather clear | urgent False | afternoon
   Route A (Main Blvd): 4.0 km, normal traffic, ~10.9 min 
   Route B (Canal Rd): 6.0 km, light traffic, ~12.0 min 

>> Simple Reflex Agent
   RULE: traffic is normal -> stay on Route A (Main Blvd)
   Actions: Pick up order ORD-101 | Ride via Route A (Main Blvd) | Hand over order
   Route: Route A (Main Blvd)   ETA: 20.9 min   (ON TIME)

>> Model-Based Reflex Agent
   STATE: weather=clear, status=accepted, last route=None
   STATE: traffic model = {'Route A (Main Blvd)': 'normal', 'Route B (Canal Rd)': 'light'}
   RULE: choose Route A (Main Blvd) (first road not jammed in model)
   Actions: Accept order ORD-101 | Pick up food (status: picked_up) | Ride via Route A (Main Blvd) | Deliver (status: delivered)
   Route: Route A (Main Blvd)   ETA: 20.9 min   (ON TIME)

>> Goal-Based Agent
   GOAL: deliver ORD-101 within 40 min
     predict Route A (Main Blvd): arrive in 20.9 min -> goal met
   Selected Route A (Main Blvd) because it achieves the goal
   Actions: Accept order ORD-101 | Pick up food | Ride via Route A (Main Blvd) | Deliver order
   Route: Route A (Main Blvd)   ETA: 20.9 min   (ON TIME)

>> Utility-Based Agent
   weights: {'time': 0.45, 'distance': 0.15, 'traffic': 0.2, 'cost': 0.2}
     Route A (Main Blvd): time=20.9m dist=4.0km traffic=normal cost=Rs48 -> U=0.669
     Route B (Canal Rd): time=22.0m dist=6.0km traffic=light cost=Rs72 -> U=0.673
   Best utility: Route B (Canal Rd) (U=0.673)
   Actions: Accept order ORD-101 | Pick up food | Ride via Route B (Canal Rd) | Deliver order
   Route: Route B (Canal Rd)   ETA: 22.0 min   (ON TIME)

>> Learning Agent
     learned estimate Route A (Main Blvd): 11.2 min (2.80 min/km)
     learned estimate Route B (Canal Rd): 12.0 min (2.00 min/km)
   Best known route: Route A (Main Blvd)
   FEEDBACK: expected 11.2 min, actual 11.2 min
   Updated ('normal', 'clear') -> 2.80 min/km
   Actions: Accept order ORD-101 | Pick up food | Ride via Route A (Main Blvd) | Deliver order | Record feedback for next time
   Route: Route A (Main Blvd)   ETA: 21.2 min   (ON TIME)

>> Hierarchical Agent
   TOP GOAL: Deliver order ORD-101
     [1] accept_order: order accepted
     [2] choose_route: Route A (Main Blvd) (10.9 min ride)
     [3] pick_up_food: wait 10 min at restaurant
     [4] deliver_order: leave restaurant, follow Route A, reach customer
     [5] confirm_delivery: on time (20.9/40 min), ask for rating
   Actions: t=0m  Accept order | t=0m  Plan route -> Route A (Main Blvd) | t=10m  Pick up food | t=21m  Deliver order | t=21m  Confirm delivery
   Route: Route A (Main Blvd)   ETA: 20.9 min   (ON TIME)

>> Contextual Agent
   CONTEXT: {'rush_hour': False, 'raining': False, 'urgent': False, 'food_type': 'hot', 'note': 'Leave at the gate', 'vehicle': 'bike'}
     normal order -> balance time and toll
   Actions: Accept order ORD-101 | Use insulated hot bag | Pick up food | Ride via Route A (Main Blvd) | Customer note: Leave at the gate | Deliver order
   Route: Route A (Main Blvd)   ETA: 20.9 min   (ON TIME)

======================================================================
Case 2: Heavy traffic, multiple routes
--------------------------------------
Order ORD-102: Large pizza, 1.5L drink | prep 15m | deadline 40m | weather cloudy | urgent False | evening rush
   Route A (Main Blvd): 4.0 km, heavy traffic, ~24.0 min 
   Route B (Canal Rd): 6.5 km, light traffic, ~13.0 min 
   Route C (Ring Rd): 5.0 km, normal traffic, ~13.6 min toll Rs60

>> Simple Reflex Agent
   RULE: traffic on Route A (Main Blvd) is heavy -> switch to Route B (Canal Rd)
   Actions: Pick up order ORD-102 | Ride via Route B (Canal Rd) | Hand over order
   Route: Route B (Canal Rd)   ETA: 28.0 min   (ON TIME)

>> Model-Based Reflex Agent
   STATE: weather=cloudy, status=accepted, last route=Route A (Main Blvd)
   STATE: traffic model = {'Route A (Main Blvd)': 'heavy', 'Route B (Canal Rd)': 'light', 'Route C (Ring Rd)': 'normal'}
   RULE: choose Route B (Canal Rd) (first road not jammed in model)
   Actions: Accept order ORD-102 | Pick up food (status: picked_up) | Ride via Route B (Canal Rd) | Deliver (status: delivered)
   Route: Route B (Canal Rd)   ETA: 28.0 min   (ON TIME)

>> Goal-Based Agent
   GOAL: deliver ORD-102 within 40 min
     predict Route A (Main Blvd): arrive in 39.0 min -> goal met
   Selected Route A (Main Blvd) because it achieves the goal
   Actions: Accept order ORD-102 | Pick up food | Ride via Route A (Main Blvd) | Deliver order
   Route: Route A (Main Blvd)   ETA: 39.0 min   (ON TIME)

>> Utility-Based Agent
   weights: {'time': 0.45, 'distance': 0.15, 'traffic': 0.2, 'cost': 0.2}
     Route A (Main Blvd): time=39.0m dist=4.0km traffic=heavy cost=Rs48 -> U=0.4
     Route B (Canal Rd): time=28.0m dist=6.5km traffic=light cost=Rs78 -> U=0.615
     Route C (Ring Rd): time=28.6m dist=5.0km traffic=normal cost=Rs120 -> U=0.524
   Best utility: Route B (Canal Rd) (U=0.615)
   Actions: Accept order ORD-102 | Pick up food | Ride via Route B (Canal Rd) | Deliver order
   Route: Route B (Canal Rd)   ETA: 28.0 min   (ON TIME)

>> Learning Agent
     learned estimate Route A (Main Blvd): 14.0 min (3.50 min/km)
     learned estimate Route B (Canal Rd): 13.0 min (2.00 min/km)
     learned estimate Route C (Ring Rd): 14.0 min (2.80 min/km)
   Best known route: Route B (Canal Rd)
   FEEDBACK: expected 13.0 min, actual 13.1 min
   Updated ('light', 'clear') -> 2.00 min/km
   Actions: Accept order ORD-102 | Pick up food | Ride via Route B (Canal Rd) | Deliver order | Record feedback for next time
   Route: Route B (Canal Rd)   ETA: 28.0 min   (ON TIME)

>> Hierarchical Agent
   TOP GOAL: Deliver order ORD-102
     [1] accept_order: order accepted
     [2] choose_route: Route B (Canal Rd) (13.0 min ride)
     [3] pick_up_food: wait 15 min at restaurant
     [4] deliver_order: leave restaurant, follow Route B, reach customer
     [5] confirm_delivery: on time (28.0/40 min), ask for rating
   Actions: t=0m  Accept order | t=0m  Plan route -> Route B (Canal Rd) | t=15m  Pick up food | t=28m  Deliver order | t=28m  Confirm delivery
   Route: Route B (Canal Rd)   ETA: 28.0 min   (ON TIME)

>> Contextual Agent
   CONTEXT: {'rush_hour': True, 'raining': False, 'urgent': False, 'food_type': 'hot', 'note': '', 'vehicle': 'bike'}
     rush hour -> add 20% buffer to heavy/normal roads
     normal order -> balance time and toll
   Actions: Accept order ORD-102 | Use insulated hot bag | Pick up food | Ride via Route B (Canal Rd) | Deliver order
   Route: Route B (Canal Rd)   ETA: 28.0 min   (ON TIME)

======================================================================
Case 3: Heavy traffic, rain, urgent
-----------------------------------
Order ORD-103: Biryani + ice cream | prep 8m | deadline 30m | weather rain | urgent True | evening rush
   Route A (Main Blvd): 4.0 km, heavy traffic, ~32.0 min 
   Route C (Underpass): 5.0 km, normal traffic, ~18.2 min flood prone
   Route B (Canal Rd): 6.0 km, light traffic, ~16.0 min 

>> Simple Reflex Agent
   RULE: traffic on Route A (Main Blvd) is heavy -> switch to Route C (Underpass)
   RULE: it is raining -> ride slowly, cover food bag
   RULE: order is urgent -> priority delivery
   Actions: Pick up order ORD-103 | Cover food bag and ride slowly | Mark as priority | Ride via Route C (Underpass) | Hand over order
   Route: Route C (Underpass)   ETA: 26.2 min   (ON TIME)

>> Model-Based Reflex Agent
   STATE: weather=rain, status=accepted, last route=Route B (Canal Rd)
   STATE: traffic model = {'Route A (Main Blvd)': 'jam', 'Route B (Canal Rd)': 'light', 'Route C (Ring Rd)': 'normal', 'Route C (Underpass)': 'normal'}
   RULE: rain in state -> only keep light-traffic roads
   RULE: Route B (Canal Rd) still fine -> keep current route
   Actions: Accept order ORD-103 | Pick up food (status: picked_up) | Cover food bag, ride slowly | Ride via Route B (Canal Rd) | Deliver (status: delivered)
   Route: Route B (Canal Rd)   ETA: 24.0 min   (ON TIME)

>> Goal-Based Agent
   GOAL: deliver ORD-103 within 30 min
     predict Route A (Main Blvd): arrive in 40.0 min -> goal NOT met
     predict Route C (Underpass): arrive in 26.2 min -> goal met
   Selected Route C (Underpass) because it achieves the goal
   Actions: Accept order ORD-103 | Pick up food | Ride via Route C (Underpass) | Deliver order
   Route: Route C (Underpass)   ETA: 26.2 min   (ON TIME)

>> Utility-Based Agent
   Urgent order -> weights shifted towards time
   weights: {'time': 0.65, 'distance': 0.1, 'traffic': 0.15, 'cost': 0.1}
     Route A (Main Blvd): time=40.0m dist=4.0km traffic=heavy cost=Rs48 -> U=-0.092
     Route C (Underpass): time=26.2m dist=5.0km traffic=normal cost=Rs60 -> U=0.492
     Route B (Canal Rd): time=24.0m dist=6.0km traffic=light cost=Rs72 -> U=0.557
   Best utility: Route B (Canal Rd) (U=0.557)
   Actions: Accept order ORD-103 | Pick up food | Ride via Route B (Canal Rd) | Deliver order
   Route: Route B (Canal Rd)   ETA: 24.0 min   (ON TIME)

>> Learning Agent
     learned estimate Route A (Main Blvd): 18.0 min (4.50 min/km)
     learned estimate Route C (Underpass): 18.0 min (3.60 min/km)
     learned estimate Route B (Canal Rd): 16.2 min (2.70 min/km)
   Best known route: Route B (Canal Rd)
   FEEDBACK: expected 16.2 min, actual 16.6 min
   Updated ('light', 'rain') -> 2.72 min/km
   Actions: Accept order ORD-103 | Pick up food | Ride via Route B (Canal Rd) | Deliver order | Record feedback for next time
   Route: Route B (Canal Rd)   ETA: 24.2 min   (ON TIME)

>> Hierarchical Agent
   TOP GOAL: Deliver order ORD-103
     [1] accept_order: order accepted
     [2] choose_route: Route B (Canal Rd) (16.0 min ride)
     [3] pick_up_food: wait 8 min at restaurant
     [4] deliver_order: leave restaurant, put on rain cover, follow Route B, no stops (urgent), reach customer
     [5] confirm_delivery: on time (24.0/30 min), ask for rating
   Actions: t=0m  Accept order | t=0m  Plan route -> Route B (Canal Rd) | t=8m  Pick up food | t=24m  Deliver order | t=24m  Confirm delivery
   Route: Route B (Canal Rd)   ETA: 24.0 min   (ON TIME)

>> Contextual Agent
   CONTEXT: {'rush_hour': True, 'raining': True, 'urgent': True, 'food_type': 'cold', 'note': 'Call on arrival, patient at home', 'vehicle': 'bike'}
     rain -> avoid Route C (Underpass) (floods in rain)
     rush hour -> add 20% buffer to heavy/normal roads
     urgent/cold food -> pick fastest safe road
   Actions: Accept order ORD-103 | Use cooler bag with ice pack | Pick up food | Wear raincoat, waterproof the bag | Ride via Route B (Canal Rd) | Customer note: Call on arrival, patient at home | Deliver order
   Route: Route B (Canal Rd)   ETA: 24.0 min   (ON TIME)
```
</details>
