import cProfile


class Agent:
    def __init__(self, problem):
        self.problem = problem
        self.action_plan = []
        self.planning_index = 0

    def plan(self, current_state):
        actions = []
        return actions

    def act(self):
        if len(self.action_plan) == 0:
            #percept
            current_state= self.problem.get_current_state()
            self.action_plan = self.plan(current_state)

        if len(self.action_plan) > 0:
            action = self.action_plan[0]
            current_state_hash = self.problem.to_state()
            if type(action) == dict:
                for k in action.keys():
                    if current_state_hash in k:
                        self.action_plan = action[k]
                        action =self.action_plan[0]
                        break
            self.action_plan = self.action_plan[1:]
            return action

    def to_state(self, state):
        if type(state)==list:
            states = []
            for s in state:
                states.append(s.to_state())
            return frozenset(states)
        else:
            return state.to_state()
