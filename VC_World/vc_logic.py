from problem import Problem
import numpy as np


class Room:
    def __init__(self, position, clean):
        #Position is a vector with x and y coordinate
        self.position = position
        self.clean = clean


class Building:
    def __init__(self, size, dirt_rate, rooms = None, seed = None):
        self.size = size
        if seed is not None:
            np.random.seed(seed)
        if rooms is not None:
            self.rooms = rooms
        else:
            self.rooms = np.random.choice([0, 1], size=size[0]*size[1], p=[dirt_rate, 1-dirt_rate])
            self.rooms.resize(size[0], size[1])
        self.dirty_rooms = self.rooms.size-self.rooms.sum()

    def copy(self):
        building_copy = Building(self.size, 0, rooms=np.copy(self.rooms))
        return building_copy

    def clean(self, position):
        if not self.rooms[position]:
            self.dirty_rooms -= 1
            self.rooms[position] = 1

    def make_dirty(self, position):
        if self.rooms[position]:
            self.dirty_rooms += 1
            self.rooms[position] = 0

    def exist_room(self, position):
        if position[0] >= 0 and position[0] < self.rooms.shape[0] and position[1] >= 0 and position[1] < self.rooms.shape[1]:
            return True
        else:
            return False


class VC(Problem):
    def __init__(self, position, building, energy_spend = 0, random_action_rate = 0):
        #Position is a vector with x and y coordinate
        self.position = list(position)
        self.building = building
        self.energy_spend = energy_spend
        self.state = None
        self.random_action_rate = random_action_rate
        self.actions={"right":(VC.move_right, VC.move_left),
                      "left":(VC.move_left,VC.move_right),
                      "up":(VC.move_up,VC.move_down),
                      "down":(VC.move_down,VC.move_up),
                      "clean":(VC.clean,VC.make_dirty)}

    def copy(self):
        position_copy = self.position[:]
        building_copy = self.building.copy()
        vc_copy = VC(position_copy, building_copy, self.energy_spend)
        return vc_copy

    def act(self, action):
        random_action = np.random.random()<self.random_action_rate
        if random_action:
            self.actions[action][1](self)
        else:
            self.actions[action][0](self)
        self.state = None
        self.to_state()

    def move(self, new_position):
        self.energy_spend += 1
        if self.building.exist_room(new_position):
            self.position = new_position
            return True
        else:
            return False

    def move_right(self):
        new_position = [self.position[0] + 1, self.position[1]]
        return self.move(new_position)

    def move_left(self):
        new_position = [self.position[0] - 1, self.position[1]]
        return self.move(new_position)

    def move_up(self):
        new_position = [self.position[0], self.position[1] - 1]
        return self.move(new_position)

    def move_down(self):
        new_position = [self.position[0], self.position[1] + 1]
        return self.move(new_position)

    def clean(self):
        self.energy_spend += 1
        self.building.clean(tuple(self.position))

    def make_dirty(self):
        self.energy_spend += 1
        self.building.make_dirty(tuple(self.position))

    def to_state(self):
        if self.state is None:
            state = []
            for x in np.nditer(self.building.rooms):
                state.append(int(x))
            state.append(self.position[0])
            state.append(self.position[1])
            self.state = tuple(state)
        return self.state

    def is_goal_state(self, state):
        if state.building.rooms.sum() == state.building.rooms.size:
            return True
        else:
            return False

    def get_applicable_actions(self, state):
        actions = []
        actions.append("clean")
        if state.position[0] + 1 < state.building.size[0]:
            actions.append("right")
        if state.position[0] - 1 >= 0:
            actions.append("left")
        if state.position[1] + 1 < state.building.size[1]:
            actions.append("down")
        if state.position[1] - 1 >= 0:
            actions.append("up")
        return actions

    def perform_action(self, state, action):
        #Add more States in case of random action
        if self.random_action_rate > 0:
            new_states = []
            for a in self.actions[action]:
                new_state = state.copy()
                a(new_state)
                new_states.append(new_state)
            return new_states
        else:
            new_state = state.copy()
            self.actions[action][0](new_state)
        return new_state

    def action_cost(self, state, action, new_state):
        costs = 1
        return costs

    def eval(self, state):
        #non-consistent heuristik seed 100 - 16 energy instead of 15
        #costs = 2*(state.building.rooms.size - state.building.rooms.sum()-1)
        #consistent but weak
        #costs = state.building.rooms.size - state.building.rooms.sum()

        #consistent and dominant
        costs = 2 * (state.building.rooms.size - state.building.rooms.sum())
        if not state.building.rooms[state.position[0], state.position[1]]:
            costs -= 1
        return costs


class VCBS(VC):

    def __init__(self, position, building, energy_spend=0, random_action_rate=0, perception = False):
        self.perception = perception
        super().__init__(position, building, energy_spend, random_action_rate)

    def is_goal_state(self, state):
        for s in state:
            if s.building.rooms.sum() != s.building.rooms.size:
                return False
        return True

    def get_applicable_actions(self, state):
        for s in state:
            actions = set()
            actions.update(super().get_applicable_actions(s))
            if len(actions) == len(self.actions):
                break;
        return list(actions)

    def perform_action(self, state, action):
        new_states=[]
        created_states = []
        for s in state:
            new_state = super().perform_action(s, action)
            new_state_hash = new_state.to_state()
            if new_state_hash not in created_states:
                created_states.append(new_state_hash)
                new_states.append(new_state)
        return new_states

    def action_cost(self, state, action, new_state):
        costs = 1
        return costs

    def get_current_state(self):
        pos_states = []
        for x in range(self.building.rooms.shape[0]):
            for y in range(self.building.rooms.shape[1]):
                if not self.perception or\
                        self.building.rooms[self.position[0], self.position[1]] == self.building.rooms[x, y]:
                    state = self.copy()
                    state.position = [x, y]
                    pos_states.append(state)
        return pos_states

    def update_belief_state(self, state):
        # based on possible perceptions update the belief state
        # and return a list of lists of belief state as alternatives
        # clustering all bs with the same dirt stage on the agents position (observation)
        bs=[]
        dirty = []
        clean = []
        for s in state:
            if s.building.rooms[s.position[0], s.position[1]]:
                clean.append(s)
            else:
                dirty.append(s)
        if len(clean)>0:
            bs.append(clean)
        if len(dirty) > 0:
            bs.append(dirty)
        return bs

    def eval(self, state):
        costs = 0
        for s in state:
            costs += super().eval(s)
        return costs
