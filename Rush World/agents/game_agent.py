import cProfile


class GameAgent:
    def __init__(self, problem):
        self.problem = problem

    def plan(self, current_state):
        action = ""
        return action

    def act(self):
        # percept
        current_state = self.problem.get_current_state()
        # search

        pr = cProfile.Profile()
        pr.enable()

        action = self.plan(current_state)

        pr.disable()
        # after your program ends
        pr.print_stats(sort="calls")

        return action

    def to_state(self, state):
        if type(state) == list:
            states = []
            for s in state:
                states.append(s.to_state())
            return frozenset(states)
        else:
            return state.to_state()
