import random

from problem import Problem
import numpy as np
from copy import deepcopy


class Turns:
    """
    Manages the different phases of the game:
    1. Throw a dice
    2. select a figure to move
    3. if an obstacle was removed by the movement place the obstacle on a free field outside of the initial zone
    4. or if an opponents figure was removed the opponent has to place it in the initial squares
    """
    player1_get_step_range = 1
    player1_select_figure = 2
    player1_move_obstacle_to = 3
    player2_select_initial_square = 4
    player2_get_step_range = 5
    player2_select_figure = 6
    player2_move_obstacle_to = 7
    player1_select_initial_square = 8


class Player:
    """
    player1 = you
    player2 = opponent
    obstacle = an obstacle
    chance = the dice
    """
    player1 = 1
    player2 = -1
    obstacle = 2
    chance = 3


class Rush(Problem):
    """
    The aim of the game is to rush to the opposite side of the board with all figures before the opponent.
    Movement ranges are determined by a dice.
    You can jump over opponents figures but not over obstacles.
    Obstacles and opponents figures can be removed when moving on the same field.
    Obstacles are placed by the player that removed them
    The opponents figures are placed by the opponent on one of the free initial fields
    """

    def __init__(self, board_size, step_range, obstacle_probability, field=None, actions_per_turn=None, actions=None,
                 turn=None, last_step_range=None, player1_reached_goal_zone=0, player2_reached_goal_zone=0):
        """
        :param board_size: tuple of x and y dimension of the board. x defines also the number of figures for each player
        :param step_range: a tuple of a range of movements. Numbers are drawn evenly distributed
        :param __obstacle_probability: probability for an obstacle on each square other than the initial zone
        :param field: a numpy array of the board (0 = empty, Player.player1, Player.player2, Player.obstacle)
        :param __actions_per_turn: a dictionary with name of turns as keys and a list of actions names (only in case of
        "chance") or a dictionary of (i,j)-tuples for a certain field and action name as values
        :param __actions: a dictionary of action names and action functions to execute the action
        :param turn: integer for th current turn
        :param last_step_range: last result of a dice throw
        :param __state: an unchangeable representation
        :param player1_reached_goal_zone: How many figures of player 1 have reached the goal zone
        :param player2_reached_goal_zone: How many figures of player 2 have reached the goal zone
        """
        self.board_size = board_size
        self.step_range = step_range
        self.__obstacle_probability = obstacle_probability
        self.field = field
        if self.field is None:
            self.field = self.__generate_field(obstacle_probability)
        self.__actions_per_turn = actions_per_turn
        self.__actions = actions
        if self.__actions_per_turn is None or self.__actions is None:
            self.__actions_per_turn, self.__actions = self.__generate_actions()
        self.turn = turn
        if self.turn is None:
            self.turn = Turns.player1_get_step_range
        self.last_step_range = last_step_range
        self.__state = None
        self.player1_reached_goal_zone = player1_reached_goal_zone
        self.player2_reached_goal_zone = player2_reached_goal_zone

    def __generate_field(self, obstacle_probability):
        """generates the board"""
        field = np.zeros(self.board_size)
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                if j == 0:
                    # start player one
                    field[i, j] = Player.player1
                elif j == self.board_size[1] - 1:
                    # start player two
                    field[i, j] = Player.player2
                elif random.random() <= obstacle_probability:
                    # set obstacle
                    field[i, j] = Player.obstacle
        return field

    def get_player(self):
        """
        returns the current player
        :return: Player
        """
        if self.turn in (Turns.player1_get_step_range,
                         Turns.player2_get_step_range):
            return Player.chance
        elif self.turn in (Turns.player1_move_obstacle_to,
                           Turns.player1_select_figure,
                           Turns.player1_select_initial_square):
            return Player.player1
        else:
            return Player.player2

    def __is_goal_zone(self, position):
        """
        if a position is in the goal zone
        :param position: the position asked for
        :return: Bool
        """
        if self.get_player() == Player.player1:
            if position[1] == self.board_size[1] - 1:
                return True
        else:
            if position[1] == 0:
                return True
        return False

    def __get_step_range_factory(self, step_range):
        """
        Generates all action for get_step_ranges (dice throw)
        used in et for planning
        :param step_range: teh step range that is returned
        :return: Bool if successfully
        """

        def get_step_range(self):
            self.last_step_range = step_range
            if self.turn == Turns.player1_get_step_range:
                self.turn = Turns.player1_select_figure
            else:
                self.turn = Turns.player2_select_figure
            return True

        return get_step_range

    def __select_figure_factory(self, i, j):
        """
        Generates all actions for selecting a figure on a certain position
        :param i: Position x
        :param j: Position y
        :return: Bool if successfully
        """

        def select_figure(self):
            if Rush.is_move_possible(self, (i, j), self.last_step_range, self.get_player()):
                self.field[i, j] = 0
                new_j = j + self.get_player() * self.last_step_range
                old_item = self.field[i, new_j]
                self.field[i, new_j] = self.get_player()
                if self.__is_goal_zone((i, new_j)):
                    self.field[i, new_j] = 0
                    if self.get_player() == Player.player1:
                        self.player1_reached_goal_zone += 1
                    else:
                        self.player2_reached_goal_zone += 1
                if old_item == Player.player1:
                    self.turn = Turns.player1_select_initial_square
                elif old_item == Player.player2:
                    self.turn = Turns.player2_select_initial_square
                elif old_item == Player.obstacle and self.get_player() == Player.player1:
                    self.turn = Turns.player1_move_obstacle_to
                elif old_item == Player.obstacle and self.get_player() == Player.player2:
                    self.turn = Turns.player2_move_obstacle_to
                elif self.get_player() == Player.player1:
                    self.turn = Turns.player2_get_step_range
                else:
                    self.turn = Turns.player1_get_step_range
                return True
            return False

        return select_figure

    def __move_obstacle_to_factory(self, i, j):
        """
        Generates all actions for selecting a position for placing an obstacle
        :param i: Position x
        :param j: Position y
        :return: Bool if successfully
        """

        def move_obstacle_to(self):
            if self.field[i, j] == 0 and j > 0 and j < self.board_size[1] - 1:
                self.field[i, j] = Player.obstacle
                if self.turn == Turns.player1_move_obstacle_to:
                    self.turn = Turns.player2_get_step_range
                    return True
                else:
                    self.turn = Turns.player1_get_step_range
                    return True
            return False

        return move_obstacle_to

    def __select_initial_square_factory(self, i, j):
        """
        Generates all actions for selecting an initial position for placing a figure
        :param i: Position x
        :param j: Position y
        :return: Bool if successfully
        """

        def select_initial_square(self):
            if self.field[i, j] == 0:
                if self.get_player() == Player.player1 and j == 0:
                    self.field[i, j] = self.get_player()
                    self.turn = Turns.player1_get_step_range
                    return True
                elif self.get_player() == Player.player2 and j == self.board_size[1] - 1:
                    self.field[i, j] = self.get_player()
                    self.turn = Turns.player2_get_step_range
                    return True
            return False

        return select_initial_square

    @staticmethod
    def skip_turn(self):
        """
        Method to skip a turn if no action is possible
        :param self: state
        :return: Bool if successfully
        """
        if self.turn == Turns.player1_select_figure or self.turn == Turns.player1_move_obstacle_to:
            self.turn = Turns.player2_get_step_range
            return True
        elif self.turn == Turns.player2_select_figure or self.turn == Turns.player2_move_obstacle_to:
            self.turn = Turns.player1_get_step_range
            return True
        else:
            return False

    def __generate_actions(self):
        """
        Generates the actions for the match
        :return: actions_per_turn, actions
        """
        actions_per_turn = {}
        actions = {}
        # get_step_range
        action_list = []
        for r in range(self.step_range[0], self.step_range[1] + 1):
            func = self.__get_step_range_factory(r)
            key = f"get_step_range_{r}"
            setattr(type(self), key, func)
            action_list.append(key)
            actions[key] = func
        actions_per_turn[Turns.player1_get_step_range] = action_list
        actions_per_turn[Turns.player2_get_step_range] = action_list

        # select_figure and move_obstacle
        action_dict1 = {}
        action_dict2 = {}
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                func = self.__select_figure_factory(i, j)
                key = f'select_figure_{i}_{j}'
                setattr(type(self), key, func)
                action_dict1[(i, j)] = key
                actions[key] = func
                func = self.__move_obstacle_to_factory(i, j)
                key = f'move_obstacle_to_{i}_{j}'
                setattr(type(self), key, func)
                action_dict2[(i, j)] = key
                actions[key] = func
        action_dict1[-1, -1] = "skip_turn"
        action_dict2[-1, -1] = "skip_turn"
        actions["skip_turn"] = self.skip_turn
        actions_per_turn[Turns.player1_select_figure] = action_dict1
        actions_per_turn[Turns.player2_select_figure] = action_dict1
        actions_per_turn[Turns.player1_move_obstacle_to] = action_dict2
        actions_per_turn[Turns.player2_move_obstacle_to] = action_dict2

        # select_square
        action_dict1 = {}
        action_dict2 = {}
        for i in range(self.board_size[0]):
            func = self.__select_initial_square_factory(i, 0)
            key = f'select_initial_square_{i}_{0}'
            setattr(type(self), key, func)
            action_dict1[(i, 0)] = key
            actions[key] = func
            func = self.__select_initial_square_factory(i, self.board_size[1] - 1)
            key = f'select_initial_square_{i}_{self.board_size[1] - 1}'
            setattr(type(self), key, func)
            action_dict2[(i, self.board_size[1] - 1)] = key
            actions[key] = func
        actions_per_turn[Turns.player1_select_initial_square] = action_dict1
        actions_per_turn[Turns.player2_select_initial_square] = action_dict2
        return actions_per_turn, actions

    @staticmethod
    def is_move_possible(state, position, step_range, player):
        """
        Is a movement of "range" from "position" of "player" in "state" possible?
        :return: Bool
        """
        i = position[0]
        new_j = position[1] + player * step_range
        # move outside board?
        if new_j < 0 or new_j >= state.board_size[1]:
            return False
        # cannot move on same field than piece of same team
        if state.field[i, new_j] == player:
            return False
        # obstacle in path?
        for j in range(min(position[1], new_j) + 1, max(position[1], new_j)):
            if state.field[i, j] == Player.obstacle:
                return False

        return True

    def copy(self):
        """
        Copies itself
        :return: a copy of Rush
        """
        rush_copy = Rush(self.board_size[:], self.step_range[:], self.__obstacle_probability, self.field.copy(),
                         self.__actions_per_turn, self.__actions,
                         turn=self.turn, last_step_range=self.last_step_range,
                         player1_reached_goal_zone=self.player1_reached_goal_zone,
                         player2_reached_goal_zone=self.player2_reached_goal_zone)
        return rush_copy

    def act(self, action):
        """
        Acts in the real environment and updates the __state variable
        :param action: action name as string
        :return: None
        """
        self.__actions[action](self)
        self.__state = None
        self.to_state()

    def to_state(self):
        """
        Creates a tuple representation of itself and saved it in __state
        :return: tuple representation
        """
        if self.__state is None:
            state = []
            for x in np.nditer(self.field):
                state.append(int(x))
            state.append(self.last_step_range)
            state.append(self.turn)
            self.__state = tuple(state)
        return self.__state

    def get_applicable_actions(self, state):
        actions = {}
        player = state.get_player()
        actions_to_filter = deepcopy(state.__actions_per_turn[state.turn])
        if state.turn == Turns.player1_get_step_range or state.turn == Turns.player2_get_step_range:
            return actions_to_filter, Player.chance
        elif state.turn == Turns.player1_select_initial_square or state.turn == Turns.player2_select_initial_square:
            for i in range(state.board_size[0]):
                if state.field[
                    i, 0 if state.turn == Turns.player1_select_initial_square else state.board_size[1] - 1] != player:
                    actions[i, 0 if state.turn == Turns.player1_select_initial_square else state.board_size[1] - 1] = \
                        actions_to_filter[
                            i, 0 if state.turn == Turns.player1_select_initial_square else state.board_size[1] - 1]
            return actions, player * -1

        for i in range(state.board_size[0]):
            for j in range(state.board_size[1]):
                if (state.turn == Turns.player1_select_figure or state.turn == Turns.player2_select_figure) and \
                        state.field[i, j] == state.get_player() and Rush.is_move_possible(state, (i, j),
                                                                                          state.last_step_range,
                                                                                          state.get_player()):
                    actions[i, j] = actions_to_filter[i, j]
                elif (state.turn == Turns.player1_move_obstacle_to or state.turn == Turns.player2_move_obstacle_to) and \
                        state.field[i, j] == 0 and j != 0 and j != state.board_size[1] - 1:
                    actions[i, j] = actions_to_filter[i, j]
        if len(actions) == 0:
            actions[-1, -1] = actions_to_filter[-1, -1]
        return actions, player

    def perform_action(self, state, action):
        new_state = state.copy()
        self.__actions[action](new_state)
        return new_state

    def action_cost(self, state, action, new_state):
        costs = 1
        return costs

    def is_goal_state(self, state):
        if self.player1_reached_goal_zone == 4:
            return 1
        elif self.player2_reached_goal_zone == 4:
            return -1
        else:
            return False

    def eval(self, state):
        evaluation = self.player1_reached_goal_zone - self.player2_reached_goal_zone
        return evaluation


class Environment:

    def __init__(self, board_size=(4, 8), step_range=(1, 1), obstacle_probability=0.0, width_room=80, height_room=80):
        self.rush = Rush(board_size, step_range, obstacle_probability)
        self.width_room = width_room
        self.height_room = height_room
