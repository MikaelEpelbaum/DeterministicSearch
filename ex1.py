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
        self.map = np.array(initial["map"])
        taxis = initial["taxis"]
        # fuel level changing bugs the priority queue
        taxis = {taxi: (taxis.get(taxi), []) for taxi in taxis.keys()}
        self.fuels = {taxi: (taxis.get(taxi)[0]['fuel']) for taxi in taxis.keys()}
        self.capacity = {taxi: (taxis.get(taxi)[0]['capacity']) for taxi in taxis.keys()}
        passengers = initial["passengers"]
        # boolean False to indicate passenger wasn't picked yet
        passengers = {passenger: (passengers.get(passenger), False) for passenger in passengers.keys()}
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
        passengers = state["passengers"]
        passengers_to_collect = {passenger for passenger in passengers if not passengers.get(passenger)[1]}
        refuel = []
        global_actions = {}
        impossibles = tuple(zip(*np.where(self.map == 'I')))
        for taxi, taxi_details in taxis_dict.items():
            curr_pos = np.asarray(taxi_details[0]["location"])
            # curr_fuel = taxi_details[2]
            curr_occupancy = len(taxi_details[1])
            all_moves = [curr_pos + np.asarray(step) for step in steps]
            # all possible direction movement listing
            for move in all_moves:
                if 0 <= move[0] < n and 0 <= move[1] < m and tuple(move) not in impossibles:
                    taxis_actions[taxi].append(("move", taxi, tuple(move)))
            # passegers that can be piked listing
            passengers_to_pick = [passenger for passenger in passengers_to_collect if tuple(passengers[passenger][0]["location"]) == tuple(curr_pos)]
            for pas in passengers_to_pick:
                taxis_actions[taxi].append(("pick up", taxi, pas))
            # does the taxi has passengers?
            if len(taxis_dict[taxi][1]) > 0:
                to_drop_off = [passenger for passenger, loc_pos in passengers.items() if loc_pos[0]["destination"] == loc_pos[0]["location"] and passenger in taxis_dict[taxi][1]]
                for pas in to_drop_off:
                    taxis_actions[taxi].append(("drop off", taxi, pas))
            if self.map[tuple([taxis_dict[taxi][0]["location"]][0])] == 'G':
                refuel = [("refuel", taxi)]

            global_actions[taxi] = [taxis_actions[taxi] + [("wait", taxi)] + refuel]

        all_moves = [global_actions[act][0] for act in global_actions.keys()]
        cartesian = [element for element in itertools.product(*all_moves)]
                    

        # todo: remove impossible moves if two taxis go to the same tile

        return cartesian
        # return [a for a in itertools.product(*cartesian)]

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        state = eval(state)
        state = json.loads(json.dumps(state))

        # if action[0][2] == (3, 0) and action[1][2] == (0, 0):
        # if action[0][0] == "pick up" and action[0][2] == "Tamar" and action[1][0] == "pick up" and action[1][2] == "Iris":
        # if len(action[0]) > 2 and len(action[1]) > 2:
        #     if action[0][0] == "pick up" and action[0][2] == "Tamar" and action[1][0] == "pick up" and action[1][2] == "Iris":
        #         if state["taxis"]["taxi 1"][0]["fuel"] == 4 and state["taxis"]["taxi 2"][0]["fuel"] == 5:
        #             print("ok")
        # if len(action[0]) > 2 and len(action[1]) > 2:
        #     if action[0][2] == (3, 1) and action[1][2] == (0, 1):
        #         if state["taxis"]["taxi 1"][0]["fuel"] == 4 and state["taxis"]["taxi 2"][0]["fuel"] == 5:
        #             print('')
        # if len(action[0]) > 2 and len(action[1]) > 2:
        #     if action[0][0] == "pick up" and action[0][2] == "Daniel" and "Tamar" in state["taxis"]["taxi 1"][1] and "Iris" in state["taxis"]["taxi 2"][1]:
        #         print('k')
        # if len(action[0]) > 2 and len(action[1]) > 2:
        #     if "Tamar" in state["taxis"]["taxi 1"][1] and "Daniel" in state["taxis"]["taxi 1"][1] and "Iris" in state["taxis"]["taxi 2"][1]:
        #         if tuple(state["taxis"]["taxi 1"][0]['location']) == (3,1) and tuple(state["taxis"]["taxi 2"][0]['location']) == (0,2):
        #             print('k')
        # if len(action[0]) > 2 and len(action[1]) > 2:
        #     if "Tamar" in state["taxis"]["taxi 1"][1] and "Daniel" in state["taxis"]["taxi 1"][1] and "Iris" in state["taxis"]["taxi 2"][1]:
        #         if tuple(state["taxis"]["taxi 1"][0]['location']) == (2, 1) and tuple(state["taxis"]["taxi 2"][0]['location']) == (0,3):
        #             print('k')
        # if len(action[0]) > 2 and len(action[1]) > 2:
        #     if "Tamar" in state["taxis"]["taxi 1"][1] and "Daniel" in state["taxis"]["taxi 1"][1] and "Iris" in state["taxis"]["taxi 2"][1]:
        #         if tuple(state["taxis"]["taxi 1"][0]['location']) == (2, 1) and tuple(state["taxis"]["taxi 2"][0]['location']) == (1,3):
        #             print('k')


        # it's a for because there may be more than one taxi thus actions
        for taxi_a in action:

            if len(taxi_a) < 3:
                act = taxi_a[0]
                taxi = taxi_a[1]
                if act == "wait":
                    continue
                else:
                    state["taxis"][taxi][0]["fuel"] = self.fuels.get(taxi)
                    continue

            taxi = taxi_a[1]

            if taxi_a[0] == "pick up" and len(state["taxis"][taxi][1]) < state["taxis"][taxi][0]["capacity"]:
                passenger = taxi_a[2]
                state["taxis"][taxi][1].append(passenger)
                state["passengers"][passenger][1] = True

            if taxi_a[0] == "move" and state["taxis"][taxi][0]["fuel"] > 0:
                state["taxis"][taxi][0]["location"] = list(taxi_a[2])
                state["taxis"][taxi][0]["fuel"] = state["taxis"][taxi][0]["fuel"] - 1
                passengers = state["taxis"][taxi][1]
                if len(passengers) > 0:
                    for passenger in passengers:
                        state["passengers"][passenger][0]["location"] = list(taxi_a[2])

            if taxi_a[0] == "drop off":
                passenger = taxi_a[2]
                del state["passengers"][passenger]
                state['taxis'][taxi][1].remove(passenger)
                state['remains'] -= 1

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
        sum_D_i = 0
        sum_T_i = 0
        sum_of_capacity = 0
        for passenger in state["passengers"]:
            if not state["passengers"][passenger][1]:
                sum_D_i += self.manhattan(state["passengers"][passenger][0]["location"], state["passengers"][passenger][0]["destination"])
            else:
                sum_T_i += self.manhattan(state["passengers"][passenger][0]["location"], state["passengers"][passenger][0]["destination"])

        for taxi in state["taxis"]:
            sum_of_capacity += self.capacity.get(taxi)
        return(sum_D_i + sum_T_i)/sum_of_capacity

    #     """
    #     This is a slightly more sophisticated Manhattan heuristic
    #     """
    #     state = eval(node.state)
    # #  sum(D(I))   manhattan distance unpicked passengers from destination
    #     passengers_names = list(state["passengers"].keys())
    #     picked_passengers = self.flatten([tax[1][1] for tax in [taxi for taxi in state["taxis"].items()]])
    #     delivered_passengers = []
    #     for passenger in state["passengers"]:
    #         passeng = state["passengers"][passenger]
    #         if passeng["location"] == passeng["destination"]:
    #             # is passenger in taxi?
    #             for taxi in state["taxis"]:
    #                 if passenger in taxi[1]:
    #                     break
    #             delivered_passengers.append(passenger)
    #     picked_or_delivered = picked_passengers + delivered_passengers
    #     unpicked_passengers = self.subtract(passengers_names, picked_or_delivered)
    #     unpicked_passengers_manhattan = 0
    #     for pas in unpicked_passengers:
    #         x = state["passengers"][pas]
    #         unpicked_passengers_manhattan += self.manhattan(x["location"], x["destination"])
    #     picked_and_destination_manhattan = 0
    #     for pas in picked_or_delivered:
    #         x = state["passengers"][pas]
    #         picked_and_destination_manhattan += self.manhattan(x["location"], x["destination"])
    #
    #     taxis_sum = len(state["taxis"])
    #     return (unpicked_passengers_manhattan+ picked_and_destination_manhattan)/taxis_sum

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

