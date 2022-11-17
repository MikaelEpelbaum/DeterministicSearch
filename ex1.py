import search
import random
import math
import numpy as np
import itertools


ids = ["111111111", "111111111"]


class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""

        # do we really need the self.taxis_start?
        self.taxis_start =initial["taxis"].copy()
        taxis = initial["taxis"]
        taxis = {taxi: (taxis.get(taxi), []) for taxi in taxis.keys()}
        passengers = initial["passengers"]
        self.map = np.array(initial["map"])
        state = {'taxis': taxis, 'passengers': passengers, 'remains': len(passengers)}

        search.Problem.__init__(self, repr(state))
        #search.Problem.__init__(self, initial)
        
    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        state = eval(state)
        n, m = np.shape(self.map)
        steps = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        taxis_dict = state["taxis"]
        taxis_actions = {taxi: [] for taxi in taxis_dict.keys()}
        passengers_to_collect = set(state["passengers"].keys())
        for taxi, taxi_details in taxis_dict.items():
            curr_pos = np.asarray(taxi_details[0]["location"])
            curr_fuel = taxi_details[0]["fuel"]
            curr_capacity = len(taxi_details[1])
            all_moves = [curr_pos + np.asarray(step) for step in steps]
            for move in all_moves:
                if 0 <= move[0] < n and 0 <= move[1] < m and self.map[move[0]][move[1]] == 'P':
                    taxis_actions[taxi].append(("move", taxi, tuple(move)))
            if taxis_dict[taxi][0]["capacity"] - curr_capacity > 0:
                passengers_to_pick = \
                    [passenger for passenger, pos in state["passengers"].items() if pos == tuple(curr_pos) and passenger in passengers_to_pick]
                if len(passengers_to_pick) > 0:
                    taxis_actions[taxi].append(("pick up", taxi, passengers_to_pick[0]))
                    passengers_to_collect.remove(passengers_to_pick[0])
            if len(taxis_dict[taxi][1]) > 0:
                passengers = [passenger for passenger, loc_pos in state["passengers"].items() if loc_pos["destination"] == tuple(curr_pos)]
                for c in passengers:
                    for p in taxis_dict[taxi][1]:
                        if p in state["clients"][c][0]:
                            taxis_actions[taxi].append(("drop off", taxi, c, p))
                            break
                    else:
                        continue
                    break
        all_actions = [a for a in taxis_actions.values()]
        impossibles = tuple(zip(*np.where(self.map == 'I')))
        possible_acctions = [action for action in all_actions[0] if action[2] not in impossibles]
        waits = list(("wait", taxi) for taxi in taxis_dict.keys())
        possible_acctions = [possible_acctions + waits]
        return [a for a in itertools.product(*possible_acctions)]




    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return 0

    def h_1(self, node):
        """
        This is a simple heuristic
        """

    def h_2(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_taxi_problem(game):
    return TaxiProblem(game)

