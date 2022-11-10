import numpy as np
import random
import math
from problem import Problem


class WumpusWorld(Problem):

    def __init__(self, n, m, pit_rate = 0.2, player_pos = (0,0), player_direction = np.array((0,1)),
                 fields_occupied = {(0, 0)}, pits = None, wumpus_pos = None, gold_pos = None, wumpus_is_dead= False, player_has_gold = False,
                 player_climbed_out = False, player_has_arrow = True, points = 0, player_perception = None):
        self.n=n
        self.m=m
        self.player_pos = player_pos
        self.player_direction = player_direction #in (-1,0),(0,-1),(1,0),(0,1)
        self.fields_occupied = fields_occupied
        self.fields = {(x,y):[] for x in range(n) for y in range(m)}
        if pits is None:
            self.pits_pos = self.generate_pits(pit_rate)
        else:
            self.pits_pos = pits
        if wumpus_pos is None and not wumpus_is_dead:
            self.wumpus_pos = self.get_free_field()
        else:
            self.wumpus_pos = wumpus_pos
        if gold_pos is None and not player_has_gold:
            self.gold_pos = self.get_free_field()
        else:
            self.gold_pos = gold_pos
        self.wumpus_is_dead = wumpus_is_dead
        self.player_has_gold = player_has_gold
        self.player_climbed_out = player_climbed_out
        self.player_has_arrow = player_has_arrow
        self.points = points
        self.actions={"right":WumpusWorld.act_turn_right,
                      "left":WumpusWorld.act_turn_left,
                      "forward":WumpusWorld.act_forward,
                      "shoot":WumpusWorld.act_shoot,
                      "grab":WumpusWorld.act_grab,
                      "climb":WumpusWorld.act_climb}

        if player_perception is None:
            self.player_perception = {}
            self.percept()
        else:
            self.player_perception = player_perception
        self.scream_heard = False


    def __str__(self):
        output =" "
        for j in range(self.m):
            output +="_"
        for i in range(self.n):
            output += "\n"
            output += "|"
            for j in range(self.m):
                if self.wumpus_pos == (self.n-i, j+1):
                    output += "W"
                elif self.gold_pos == (self.n-i, j+1):
                    output += "G"
                elif self.player_pos == (self.n-i, j+1):
                    output += "H"
                elif (self.n-i, j+1) in self.pits_pos:
                    output += "P"
                else:
                    output += " "
            output += "|"
        output += "\n "
        for j in range(self.m):
            output +="_"
        return output


    def draw_perception(self):
        for p in self.player_perception:
            print (str(self.player_perception[p]))


    def act(self, action):
        self.scream_heard = False
        self.actions[action](self)
        #self.state = None
        #self.to_state

    def copy(self):
        player_perception_copy = {}
        for pos, percept in self.player_perception.items():
            player_perception_copy[pos] = percept.copy()

        ww_copy = WumpusWorld(self.n, self.m, 0.0, self.player_pos, self.player_direction[:],
                              self.fields_occupied.copy(), self.pits_pos.copy(), self.wumpus_pos, self.gold_pos,
                              self.wumpus_is_dead, self.player_has_gold, self.player_climbed_out, self.player_has_arrow,
                              self.points, player_perception_copy)
        return ww_copy

    def to_state(self):
        state = []

        state.append(self.n)
        state.append(self.m)
        state.append(self.player_pos[0])
        state.append(self.player_pos[1])
        state.append(self.player_direction[0])
        state.append(self.player_direction[1])
        for pit in self.pits_pos:
            state.append(pit[0])
            state.append(pit[1])
        state.append(self.wumpus_pos[0])
        state.append(self.wumpus_pos[1])
        state.append(self.gold_pos[0])
        state.append(self.gold_pos[1])
        state.append(self.player_has_gold)
        state.append(self.player_has_arrow)
        state.append(self.player_climbed_out)
        state.append(self.points)
        state.append((str(self.player_perception)))

        return state

    def percept(self):
        for p in self.player_perception:
            self.player_perception[p].player = False

        if self.player_pos not in self.player_perception.keys():
            self.player_perception[self.player_pos] = self.FieldPerception(self.player_pos)
            self.player_perception[self.player_pos].player  = True
        neighbours = self.get_neighbours(self.player_pos)
        if len(self.pits_pos.intersection(neighbours)) > 0:
            self.player_perception[self.player_pos].breeze = True
        if self.wumpus_pos in neighbours:
            self.player_perception[self.player_pos].stench = True
        if self.gold_pos == self.player_pos:
            self.player_perception[self.player_pos].gold = True

    def get_neighbours(self, pos):
        neighbours = set()
        pos_neighbours = set({tuple(np.array(pos)+np.array((0, 1))), tuple(np.array(pos)+np.array((0, -1))),
                              tuple(np.array(pos)+np.array((1, 0))),tuple(np.array(pos)+np.array((-1, 0)))})
        for n in pos_neighbours:
            if n in self.fields:
                neighbours.add(n)
        return neighbours

    def generate_pits(self, probability):
        pits = set({})
        for field in set(self.fields.keys()).difference(self.fields_occupied):
            if np.random.random()<probability:
                pits.add(field)
                self.fields_occupied.add(field)
        return pits

    def get_free_field(self):
        free_fields = set(self.fields.keys()).difference(self.fields_occupied)
        if len(free_fields) == 0:
            return None
        free_field = tuple(random.sample(free_fields, k=1)[0])
        self.fields_occupied.add(free_field)
        return free_field

    def act_forward(self):
        self.points -=1
        if tuple(np.array(self.player_pos) + self.player_direction) in self.fields:
            self.player_pos = tuple(np.array(self.player_pos) + self.player_direction)
        if self.player_pos is not None:
            self.percept()
        if self.player_pos == self.wumpus_pos:
            self.player_death("Wumpus")
        if self.player_pos in self.pits_pos:
            self.player_death("Pit")

    def player_death(self, cause):
        self.points -= 1000
        self.player_pos = None
        print(f"Died with: {self.points} points and {int(self.player_has_gold)} gold killed by {cause}")

    def act_turn_right(self):
        self.points -= 1
        self.player_direction = self.__turn(self.player_direction, math.pi/2)

    def act_turn_left(self):
        self.points -= 1
        self.player_direction = self.__turn(self.player_direction, -math.pi/2)

    def __turn(self, pos, angle):
        x = round(pos[0] * math.cos(angle) - pos[1] * math.sin(angle))
        y = round(pos[0] * math.sin(angle) + pos[1] * math.cos(angle))
        return np.array((int(x), int(y)))

    def act_grab(self):
        self.points -= 1
        if self.player_pos == self.gold_pos and not self.player_has_gold:
            self.player_has_gold = True
            self.gold_pos = None

    def act_shoot(self):
        self.points -= 11
        if self.player_has_arrow:
            self.player_has_arrow = False
            if self.wumpus_pos != None:
                pos_arrow = self.player_pos
                while pos_arrow in self.fields:
                    pos_arrow = tuple(pos_arrow + self.player_direction)
                    if pos_arrow == self.wumpus_pos:
                        self.wumpus_pos = None
                        self.scream_heard = True
                        self.wumpus_is_dead = True
                        break

    def act_climb(self):
        self.points -= 1
        if self.player_pos == (0,0):
            if self.player_has_gold:
                self.points += 1000
            self.player_climbed_out = True
            print(f"Escaped with: {self.points} points and {int(self.player_has_gold)} gold")


    def is_goal_state(self, state):
        if state.player_has_gold and state.player_climbed_out:
            return True
        else:
            return False

    def get_applicable_actions(self, state):
        actions = []
        actions.append("right")
        actions.append("left")
        if state.gold_pos == state.player_pos:
            actions.append("grab")
        if state.player_pos == (0,0):
            actions.append("climb")
        if state.player_has_arrow:
            actions.append("shoot")
        if state.player_direction[0] + state.player_pos[0] < state.n \
                and state.player_direction[0] + state.player_pos[0] >= 0\
                and state.player_direction[1] + state.player_pos[1] < state.m \
                and state.player_direction[1] + state.player_pos[1] >= 0:
            actions.append("forward")
        return actions

    def get_perception(self, state):
        perceptions =[]
        perceptions.append((True,f"Agent_{int(state.player_pos[0])}_{int(state.player_pos[1])}"))
        if state.scream_heard:
            perceptions.append((True,"Scream"))
        if state.player_pos in state.player_perception.keys():
            perception_field = state.player_perception[ state.player_pos]
            if perception_field.stench:
                perceptions.append((True,"Stench"))
            else:
                perceptions.append((False, "Stench"))
            if perception_field.breeze:
                perceptions.append((True,"Breeze"))
            else:
                perceptions.append((False, "Breeze"))
            if perception_field.gold:
                perceptions.append((True,"Glitter"))
            else:
                perceptions.append((False, "Glitter"))
        return perceptions

    def get_current_state(self):
        return self.copy()

    def perform_action(self, state, action):
        new_state = state.copy()
        self.actions[action](new_state)
        return new_state

    def action_cost(self, state, action, new_state):
        #MISSING
        costs = 1
        return costs

    def eval(self, state):
        # MISSING
        costs = 0
        return costs

    class FieldPerception:

        def __init__(self, pos, wumpus = False, pitt = False, stench = False,
                     breeze = False, gold = False, player = False):
            self.pos = pos
            self.wumpus = wumpus
            self.pitt = pitt
            self.stench = stench
            self.breeze =breeze
            self.gold = gold
            self.player = player

        def __str__(self):
            return str(self.__dict__)

        def copy(self):
            field_perception_copy = WumpusWorld.FieldPerception(self.pos,self.wumpus, self.pitt, self.stench,
                                                                    self.breeze, self.gold, self.player)
            return field_perception_copy

