import cProfile
import numpy as np

class AO_Agent:
    def __init__(self, problem):
        self.problem = problem
        self.path = []
        self.action_plan = {}
        self.planning_index = 0
        self.planned_state = None

    def plan(self, current_state):
        plan = self.ao_star(current_state)
        return plan

    def ao_star(self, current_state):
        return self.or_search(current_state)

    def or_search(self, states):
        print('OR')
        if type(states) != list:
            states = [states]
        if self.problem.is_goal_state(states):
            return self.action_plan
        # wenn cycle path --> failure
        temp_path = []
        if len(self.path) == 0:
            self.path.append(states)

        for elem in self.path:
            temp_path.append([item.to_state() for item in elem])

        # check for failure / cycle
        counter = {}
        for temp_elem in temp_path:
            try:
                counter[tuple(temp_elem)] += 1
            except:
                counter[tuple(temp_elem)] = 1

        for key, value in counter.items():
            if value > 1:
                print('cycle')
                return {} #self.action_plan #todo return failure

        for i in range(len(self.problem.get_applicable_actions(states))):
            action = self.problem.get_applicable_actions(states)[i]
            new_states = self.problem.perform_action(states, action)
            self.path.append(new_states)
            self.and_search(new_states)
            self.action_plan[self.to_state(new_states)] = action
            if self.problem.is_goal_state(new_states):

                print("jawollek")
                return self.action_plan
            # stop recursion
        print("du bist am arsch")
        return self.action_plan

    '''def dfs(self, current_state, visited_states):
        for action in self.problem.get_applicable_actions(current_state):
            new_state = self.problem.perform_action(current_state, action)
            if self.to_state(new_state) not in visited_states:
                visited_states.append(self.to_state(new_state))
                if self.problem.is_goal_state(new_state):
                    return [action]
                else:
                    actions = self.dfs(new_state, visited_states)
                    if len(actions) > 0:
                        actions.insert(0, action)
                        return actions
        return []'''


    def and_search(self, states):
        print('and')
        for s in states:
            self.or_search(s)


    def act(self):
        current_state = self.problem.get_current_state()
        if self.action_plan == {}:
            self.plan(current_state)
        print("das isser")
        print(self.action_plan)

        try:
            return self.action_plan[self.to_state(current_state)]
        except:
            #self.plan(current_state)
            #return self.action_plan[self.to_state(current_state)]
            appl_actions = self.problem.get_applicable_actions(current_state)
            return np.random.choice(appl_actions)

    def to_state(self, state):
        if type(state) == list:
            states = []
            for s in state:
                states.append(s.to_state())
            return frozenset(states)
        else:
            return state.to_state()
