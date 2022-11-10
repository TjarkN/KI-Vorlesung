from agents.agent import Agent
from copy import deepcopy


class KnowledgeBase():
    def __init__(self, symbols=[], fluents = [], KB = {}):
        self.symbols = symbols
        self.fluents = fluents
        self.KB = KB
        if len(self.KB) == 0:
            for s in symbols:
                self.KB[(True, s)] = []
                self.KB[(False, s)] = []

    def copy(self):
        fluents_copy = deepcopy(self.fluents)
        symbols_copy = self.symbols[:]
        KB_copy = deepcopy(self.KB)
        return KnowledgeBase(symbols_copy, fluents_copy, KB_copy)

    def tell(self, clause, output=False):
        for signed_symbol in clause:
            if signed_symbol[1] not in self.symbols:
                #print(f"add{signed_symbol}")
                self.symbols.append(signed_symbol[1])
                self.KB[(True,signed_symbol[1])] = []
                self.KB[(False,signed_symbol[1])] = []
            if clause not in self.KB[signed_symbol]:
                self.KB[signed_symbol].append(clause)
                if output:
                    print(f"add{clause}")

    def add_fluent(self, fluent):
        self.fluents.append(fluent)

    def ask(self, clause):
        KB_ask = self.copy()
        return not KB_ask.resolution(clause)

    def activate_fluents(self, t):
        for fluent in self.fluents:
            fluent_new = []
            for literal in fluent:
                literal_new = list(literal[:])
                literal_new[1] = literal_new[1].replace("#t+1", str(t+1))
                literal_new[1] = literal_new[1].replace("#t", str(t))
                fluent_new.append(tuple(literal_new))
            self.tell(fluent_new)

    def remove_fluents(self, t):
        for fluent in self.fluents:
            fluent_new = []
            for literal in fluent:
                literal_new = list(literal[:])
                literal_new[1] = literal_new[1].replace("#t+1", str(t+1))
                literal_new[1] = literal_new[1].replace("#t", str(t))
                fluent_new.append(tuple(literal_new))
            self.remove_clauses([fluent_new])

    def remove_clauses(self, clauses):
        for clause in clauses:
            for literal in clause:
                if clause in self.KB[literal]:
                    self.KB[literal].remove(clause)

    def resolution(self, clause=None):
        #here your code
        return

    def has_double_symbol(self,clause):
        symbols = []
        for signed_symbol in clause:
            if signed_symbol[1] in symbols:
                return True
            else:
                symbols.append(signed_symbol[1])
        return False


class HybridAgent(Agent):

    def __init__(self, problem, KB, n,m):
        self.KB = KB
        self.n = n
        self.m = m
        #self.KB.resolution()
        self.t = 0
        super().__init__(problem)

    def plan(self, current_state):
        #get rid of old fluents
        if self.t>0:
            self.KB.remove_fluents(self.t-1)
        #Write perception to KB
        perceptions = self.problem.get_perception(current_state)
        for perception in perceptions:
            self.KB.tell([(perception[0], f"{perception[1]}_{self.t}")], True)
        #active new fluents
        self.KB.activate_fluents(self.t)
        pos = current_state.player_pos
        #Ask for Gold
        if self.KB.ask([(True, f"Gold_{pos[0]}_{pos[1]}")]):
            self.KB.tell([(True, f"Gold_{pos[0]}_{pos[1]}")], True)
        else:
            self.KB.tell([(False, f"Gold_{pos[0]}_{pos[1]}")], True)
        # Ask KB for secure fields
        if self.KB.ask([(True, f"OK_{max(pos[0]-1,0)}_{pos[1]}_{self.t}")]):
            #print(f"1:OK_{max(pos[0]-1,0)}_{pos[1]}_{self.t}")
            self.KB.tell([(True, f"OK_{max(pos[0]-1,0)}_{pos[1]}_{self.t}")], True)
        else:
            self.KB.tell([(False, f"OK_{max(pos[0]-1,0)}_{pos[1]}_{self.t}")], True)
        if self.KB.ask([(True, f"OK_{min(pos[0] +1,self.n-1)}_{pos[1]}_{self.t}")]):
            #print(f"2:OK_{min(pos[0] +1,3)}_{pos[1]}_{self.t}")
            self.KB.tell([(True, f"OK_{min(pos[0] +1,self.n-1)}_{pos[1]}_{self.t}")], True)
        else:
            self.KB.tell([(False, f"OK_{min(pos[0] +1,self.n-1)}_{pos[1]}_{self.t}")], True)
        if self.KB.ask([(True, f"OK_{pos[0]}_{max(pos[1]-1,0)}_{self.t}")]):
            #print(f"3:OK_{pos[0]}_{max(pos[0]-1,0)}_{self.t}")
            self.KB.tell([(True, f"OK_{pos[0]}_{max(pos[1]-1,0)}_{self.t}")], True)
        else:
            self.KB.tell([(False, f"OK_{pos[0]}_{max(pos[1]-1,0)}_{self.t}")], True)
        if self.KB.ask([(True, f"OK_{pos[0]}_{min(pos[1] +1,self.m-1)}_{self.t}")]):
            #print(f"4:OK_{pos[0]}_{min(pos[1] +1,3)}_{self.t}")
            self.KB.tell([(True, f"OK_{pos[0]}_{min(pos[1] +1,self.m-1)}_{self.t}")], True)
        else:
            self.KB.tell([(False, f"OK_{pos[0]}_{min(pos[1] +1,self.m-1)}_{self.t}")], True)
        self.t += 1


def set_up_ww(size):
    """
    Propositional Symbols
    Pit_X_Y
    Wumpus_X_Y
    B_X_Y
    S_X_Y
    Gold_X_Y
    WumpusAlive_t
    Agent_X_Y_t
    Breeze_t
    Stench_t
    Scream_t
    Glitter_t
    OK_X_Y_t
    """

    ww_KB = KnowledgeBase()
    #WumpusAlive_0"
    #ww_KB.tell([(True, "WumpusAlive_0")])
    "Not Pit in [0,0] not Pit_0_0"
    ww_KB.tell([(False, "Pit_0_0")])
    "Not Wumpus [0,0] not Wumpus_0_0"
    #ww_KB.tell([(False, "Wumpus_0_0")])

    "At least one Wumpus W_1_1 or W_1_2 or..."
    #clause = []
    #neg_clause_list = []
    #for x in range(size[0]):
    #    for y in range(size[1]):
    #        clause.append((True, f"Wumpus_{x}_{y}"))
    #        neg_clause_list.append((False, f"Wumpus_{x}_{y}"))
    #ww_KB.tell(clause)

    """
    At most one Wumpus
    not W_1_1 or not W_1_2
    not W_1_1 or not W_1_3
    ...    
    """
    #clauses = {frozenset({x, y}) for x in neg_clause_list for y in neg_clause_list if x != y}
    #for clause in clauses:
    #    ww_KB.tell(list(clause))

    for x in range(size[0]):
        for y in range(size[1]):
            """
            B_X_Y<=>Pit_X-1_Y or Pit_X+1_Y or Pit_X_Y-1 or Pit_X_Y+1 --> (not B_X_Y or Pit_X-1_Y or Pit_X+1_Y or Pit_X_Y-1 or Pit_X_Y+1)
                and (not Pit_X-1_Y or B_X_Y) and (not Pit_X+1_Y or B_X_Y) and (not Pit_X_Y-1 or B_X_Y) and (not Pit_X_Y+1or B_X_Y)

            S_X_Y<=>Wumpus_X-1_Y or Wumpus_X+1_Y or Wumpus_X_Y-1 or Wumpus_X_Y+1 --> (not S_X_Y or Wumpus_X-1_Y or Wumpus_X+1_Y or Wumpus_X_Y-1 or Wumpus_X_Y+1)
            and (not Wumpus_X-1_Y or S_X_Y) and (not Wumpus_X+1_Y or S_X_Y) and (not Wumpus_X_Y-1 or S_X_Y) and (not Wumpus_X_Y+1or S_X_Y)
            """
            clause_Pit = []
            clause_Wumpus = []
            clause_Pit.append((False, f"B_{x}_{y}"))
            clause_Wumpus.append((False, f"S_{x}_{y}"))
            if x - 1 >= 0:
                clause_Pit.append((True, f"Pit_{x - 1}_{y}"))
                clause_Wumpus.append((True, f"Wumpus_{x - 1}_{y}"))
            if x + 1 < size[0]:
                clause_Pit.append((True, f"Pit_{x + 1}_{y}"))
                clause_Wumpus.append((True, f"Wumpus_{x + 1}_{y}"))
            if y - 1 >= 0:
                clause_Pit.append((True, f"Pit_{x}_{y - 1}"))
                clause_Wumpus.append((True, f"Wumpus_{x}_{y - 1}"))
            if y + 1 < size[1]:
                clause_Pit.append((True, f"Pit_{x}_{y + 1}"))
                clause_Wumpus.append((True, f"Wumpus_{x}_{y + 1}"))
            ww_KB.tell(clause_Pit)
            #ww_KB.tell(clause_Wumpus)

            if x - 1 >= 0:
                clause_Pit = []
                clause_Pit.append((False, f"Pit_{x - 1}_{y}"))
                clause_Pit.append((True, f"B_{x}_{y}"))
                ww_KB.tell(clause_Pit)
                clause_Wumpus = []
                clause_Wumpus.append((False, f"Wumpus_{x - 1}_{y}"))
                clause_Wumpus.append((True, f"S_{x}_{y}"))
                #ww_KB.tell(clause_Wumpus)
            if x + 1 < size[0]:
                clause_Pit = []
                clause_Pit.append((False, f"Pit_{x + 1}_{y}"))
                clause_Pit.append((True, f"B_{x}_{y}"))
                ww_KB.tell(clause_Pit)
                clause_Wumpus = []
                clause_Wumpus.append((False, f"Wumpus_{x + 1}_{y}"))
                clause_Wumpus.append((True, f"S_{x}_{y}"))
                #ww_KB.tell(clause_Wumpus)
            if y - 1 >= 0:
                clause_Pit = []
                clause_Pit.append((False, f"Pit_{x}_{y - 1}"))
                clause_Pit.append((True, f"B_{x}_{y}"))
                ww_KB.tell(clause_Pit)
                clause_Wumpus = []
                clause_Wumpus.append((False, f"Wumpus_{x}_{y - 1}"))
                clause_Wumpus.append((True, f"S_{x}_{y}"))
                #ww_KB.tell(clause_Wumpus)
            if y + 1 < size[1]:
                clause_Pit = []
                clause_Pit.append((False, f"Pit_{x}_{y + 1}"))
                clause_Pit.append((True, f"B_{x}_{y}"))
                ww_KB.tell(clause_Pit)
                clause_Wumpus = []
                clause_Wumpus.append((False, f"Wumpus_{x}_{y + 1}"))
                clause_Wumpus.append((True, f"S_{x}_{y}"))
                #ww_KB.tell(clause_Wumpus)

            """
            When we percept a breeze it is on the field we are standing on
            Breeze_t and Agent_X_Y_t => B_X_Y --> not Breeze_t or not Agent_X_Y_t or B_X_Y
            """
            fluent = []
            fluent.append((False, f"Breeze_#t"))
            fluent.append((False, f"Agent_{x}_{y}_#t"))
            fluent.append((True, f"B_{x}_{y}"))
            ww_KB.add_fluent(fluent)
            """
            When we don't percept a breeze there is none on the field we are standing on
            not Breeze_t and Agent_X_Y_t => not B_X_Y --> Breeze_t or not Agent_X_Y_t or not B_X_Y
            """
            fluent = []
            fluent.append((True, f"Breeze_#t"))
            fluent.append((False, f"Agent_{x}_{y}_#t"))
            fluent.append((False, f"B_{x}_{y}"))
            ww_KB.add_fluent(fluent)

            """
            When we percept a stench it is on the field we are standing on
            Stench_t and Agent_X_Y_t => S_X_Y --> not Stench_t or not Agent_X_Y_t or S_X_Y
            """
            fluent = []
            fluent.append((False, f"Stench_#t"))
            fluent.append((False, f"Agent_{x}_{y}_#t"))
            fluent.append((True, f"S_{x}_{y}"))
            #ww_KB.add_fluent(fluent)

            """
            When we don't percept a stench there is none on the field we are standing on
            not Stench_t and Agent_X_Y_t => not S_X_Y --> Stench_t or not Agent_X_Y_t or not S_X_Y
                        """
            fluent = []
            fluent.append((True, f"Stench_#t"))
            fluent.append((False, f"Agent_{x}_{y}_#t"))
            fluent.append((False, f"S_{x}_{y}"))
            #ww_KB.add_fluent(fluent)

            """
            When we percept a glitter there is gold on the current field
            Glitter_t and Agent_X_Y_t => Gold_X_Y --> not Glitter_t or not Agent_X_Y_t or Gold_X_Y
            """
            fluent = []
            fluent.append((False, f"Glitter_#t"))
            fluent.append((False, f"Agent_{x}_{y}_#t"))
            fluent.append((True, f"Gold_{x}_{y}"))
            ww_KB.add_fluent(fluent)

    # you have to add the missing statements...

    return ww_KB
