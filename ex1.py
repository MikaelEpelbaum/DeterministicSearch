import search
import random
import math
import numpy as np
import itertools
import json


ids = ["111111111", "111111111"]
# todo: update the remains field at each drop off


class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""
    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        # do we really need the self.taxis_start?
        self.taxis_start =initial["taxis"].copy()
        taxis = initial["taxis"]
        # taxi: current state, passagengers, fuel, max capacity
        taxis = {taxi: (taxis.get(taxi), [], taxis.get(taxi)["fuel"]) for taxi in taxis.keys()}
        passengers = initial["passengers"]
        self.map = np.array(initial["map"])
        state = {'taxis': taxis, 'passengers': passengers, 'remains': len(passengers)}

        search.Problem.__init__(self, repr(state))
        
    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        state = eval(state)
        if state["remains"] == 0:
            return
        n, m = np.shape(self.map)
        steps = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        taxis_dict = state["taxis"]
        taxis_actions = {taxi: [] for taxi in taxis_dict.keys()}
        passengers_to_collect = set(state["passengers"].keys())
        refuel = []
        for taxi, taxi_details in taxis_dict.items():
            curr_pos = np.asarray(taxi_details[0]["location"])
            curr_fuel = taxi_details[2]
            curr_capacity = len(taxi_details[1])
            all_moves = [curr_pos + np.asarray(step) for step in steps]
            # all possible direction movement listing
            for move in all_moves:
                if 0 <= move[0] < n and 0 <= move[1] < m:
                    # bug: list or tuple
                    taxis_actions[taxi].append(("move", taxi, tuple(move)))
            if taxis_dict[taxi][0]["capacity"] - curr_capacity > 0:
                # passegers that can be piked listing
                passengers_to_pick = \
                    [passenger for passenger, pos in state["passengers"].items() if pos == tuple(curr_pos) and passenger in passengers_to_pick]
                # redo the following if
                if len(passengers_to_pick) > 0:
                    taxis_actions[taxi].append(("pick up", taxi, passengers_to_pick[0]))
                    passengers_to_collect.remove(passengers_to_pick[0])
            # does the taxi has passengers?
            if len(taxis_dict[taxi][1]) > 0:
                passengers = [passenger for passenger, loc_pos in state["passengers"].items() if loc_pos["destination"] == tuple(curr_pos)]
                for c in passengers:
                    for p in taxis_dict[taxi][1]:
                        if p in state["clients"][c][0]:
                            taxis_actions[taxi].append(("drop off", taxi, c, p))
                            state["remains"] = state["remains"] -1
                            break
                    else:
                        continue
                    break

            # if self.item[taxis_dict[taxi][0]["location"]] == 'G':
            if self.map[tuple([taxis_dict[taxi][0]["location"]][0])] == 'G':
                refuel = [("refuel", taxi)]
        all_actions = [a for a in taxis_actions.values()]
        impossibles = tuple(zip(*np.where(self.map == 'I')))
        possible_acctions = [action for action in all_actions[0] if action[2] not in impossibles]
        waits = list(("wait", taxi) for taxi in taxis_dict.keys())
        possible_acctions = [possible_acctions + waits + refuel]

        return [a for a in itertools.product(*possible_acctions)]

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        state = eval(state)
        state = json.loads(json.dumps(state))
        # it's a for because there may be more than one taxi thus actions
        for taxi_a in action:

            if len(taxi_a) < 3:
                taxi = taxi_a[1]
                if taxi == "wait":
                    continue
                else:
                    state["taxis"][taxi][2] = state["taxis"][taxi][0]["fuel"]
                    continue

            taxi = taxi_a[1]
            pos = state["taxis"][taxi][0]["location"]

            if taxi_a[0] == "pick up":
                passenger = taxi_a[2]
                state["taxis"][taxi][1].append(passenger)
                del (state["passengers"][passenger])

            if taxi_a[0] == "move":
                state["taxis"][taxi][0]["location"] = list(taxi_a[2])
                state["taxis"][taxi][2] = state["taxis"][taxi][2] - 1

            if taxi_a[0] == "drop off":
                passenger = taxi_a[3]
                clients = [client for client, det in state["clients"].items() if det[1] == pos and passenger in det[0]]
                for c in clients:
                    state["clients"][c][0].remove(passenger)
                state["to_drop_off"] = state["to_drop_off"] - 1
                state["taxis"][taxi][1].remove(passenger)

        return repr(state)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        s = eval(state)
        if s["remains"] > 0:
            return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return self.h_1(node)
        # return self.h_2(node)

    def h_1(self, node):
        state = eval(node.state)
        picked_undelivered_sum = sum([len(state["taxis"][taxi][1]) for taxi in state["taxis"]])
        unpicked = state["remains"] - picked_undelivered_sum
        taxis_sum = len(state["taxis"])
        return (picked_undelivered_sum*2 + unpicked)/taxis_sum

    def h_2(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """
        state = eval(node.state)
    #  sum(D(I))   manhattan distance unpicked passengers from destination
        passengers_names = list(state["passengers"].keys())
        picked_passengers = self.flatten([tax[1][1] for tax in [taxi for taxi in state["taxis"].items()]])
        delivered_passengers = []
        for passenger in state["passengers"]:
            passeng = state["passengers"][passenger]
            if passeng["location"] == passeng["destination"]:
                # is passenger in taxi?
                for taxi in state["taxis"]:
                    if passenger in taxi[1]:
                        break
                delivered_passengers.append(passenger)
        picked_or_delivered = picked_passengers + delivered_passengers
        unpicked_passengers = self.subtract(passengers_names, picked_or_delivered)
        unpicked_passengers_manhattan = 0
        for pas in unpicked_passengers:
            x = state["passengers"][pas]
            unpicked_passengers_manhattan += self.manhattan(x["location"], x["destination"])
        picked_and_destination_manhattan = 0
        for pas in picked_or_delivered:
            x = state["passengers"][pas]
            picked_and_destination_manhattan += self.manhattan(x["location"], x["destination"])

        taxis_sum = len(state["taxis"])
        return (unpicked_passengers_manhattan+ picked_and_destination_manhattan)/taxis_sum

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def manhattan(self, a, b):
        return sum(abs(val1 - val2) for val1, val2 in zip(a, b))

    def flatten(self, l):
        return [item for sublist in l for item in sublist]

    def subtract(self, x, y):
        return [item for item in x if item not in y]


def create_taxi_problem(game):
    return TaxiProblem(game)

