#! /usr/bin/python
# -*- coding: utf-8 -*-
from AI.actions import Action
from AI.state import State

from Objects.robot import Robot  # Import a base Robot
from random import shuffle

class WallE(Robot):  # Create a Robot


    def init(self):  # To initialyse your robot

        # Feel free to customize: Set the bot color in RGB
        self.setColor(250, 0, 98)
        self.setGunColor(255, 207, 255)
        self.setRadarColor(254, 95, 245)
        self.setBulletsColor(204, 0, 35)
        self.maxDepth = 5

        #Don't Change
        self.setRadarField("thin")
        self.radarVisible(True)  # if True the radar field is visible
        self.gun_to_side()
        self.lockRadar("gun")
        size = self.getMapSize()

    def run(self):  # main loop to command the bot
        """
        use this method to control the bot
        1. information from your sensors:
            - get your position: self.getPosition()
            - get enemies position: self.getPosition_enemy()
            - get left energy (max 100): self.energy_left_self()
            - get left energy of enemy: self.energy_left_enemy()
            - return true if a shot would hit the enemy: self.shot_possible_by_enemy()
            - return true if a shot by the enemy would hit you: self.shot_possible_at_enemy()
            - return the angle of your gun (looking down (0,1) equals an angle of 0: self.getGunHeading()
            - return the angle of your enemies gun (looking down (0,1) equals an angle of 0: self.getGunHeading_enemy()+
            - returns the map size (left upper corner is (0,0):  self.getMapSize
        2. possible actions
            - turns 45° to the right: self.turn_right()
            - turns 45° to the left: self.turn_left()
            - move 50 points forward: self.forward()
            - move 50 points backward: self.backwards()
            - shoots cost 3 points of energy (when the enemy is hit he gets 9 points damage and you receive 6 points cure): self.shoot()
        """
        state = State(energy_self=self.energy_left_self(),
                      energy_enemy=self.energy_left_enemy(),
                      shot_possibly_by_enemy=self.shot_possible_by_enemy(),
                      shot_possibly_at_enemy=self.shot_possible_at_enemy(),
                      pos_self=self.getPosition(),
                      pos_enemy=self.getPosition_enemy(),
                      angle_self=self.getGunHeading(),
                      angle_enemy=self.getGunHeading_enemy(),
                      map_size=self.getMapSize())
        # action = self.__minimax(state, current_depth=0)[1]
        evaluation, action = self.alpha_beta_search(state)
        if action == "turn_right":
            self.turn_right()
        elif action == "turn_left":
            self.turn_left()
        elif action == "forward":
            self.forward()
        elif action == "backward":
            self.backwards()
        elif action == "shoot":
            self.shoot()

    def alpha_beta_search(self, state):
        # player = self.problem.get_player()
        evaluation, action = self.__max_value(state=state, alpha=float('-inf'), beta=float('inf'), current_depth=0)
        return evaluation, action

    def __max_value(self, state, alpha, beta, current_depth):
        if current_depth == self.maxDepth or state.is_terminal():
            return self.eval(state)[1], ""

        v = float('-inf')
        is_max_turn = (current_depth % 2 == 0)
        possible_action = state.get_possible_actions(enemy=not is_max_turn)
        actions = list(possible_action.keys()) if type(possible_action) == dict else possible_action
        shuffle(actions)

        for a in actions:
            v2, a2 = self.__min_value(state.apply_action(state, a), alpha, beta, current_depth + 1)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def __min_value(self, state, alpha, beta, current_depth):
        if current_depth == self.maxDepth or state.is_terminal():
            return self.eval(state)[1], ""

        v = float('inf')
        is_max_turn = (current_depth % 2 == 0)
        possible_action = state.get_possible_actions(enemy=not is_max_turn)
        actions = list(possible_action.keys()) if type(possible_action) == dict else possible_action

        for a in actions:
            v2, a2 = self.__max_value(state.apply_action(state, a), alpha, beta, current_depth + 1)

            if v2 < v:
                v, move = v2, a
                beta = min(alpha, v)
            if v <= alpha:
                return v, move
        return v, move

    def __minimax(self, state: State, current_depth):
        if current_depth == self.maxDepth or state.is_terminal():
            eval = state.eval()[1]
            return eval, ""

        is_max_turn = (current_depth % 2 == 0)  # 1 if current_depth even, 0 else
        possible_action = state.get_possible_actions(enemy=not is_max_turn)
        actions = list(possible_action.keys()) if type(possible_action) == dict else possible_action

        shuffle(actions)  # randomness
        best_value = float('-inf') if is_max_turn else float('inf')
        action_target = ""
        for action in actions:
            new_state = state.apply_action(enemy=not is_max_turn, action=action)
            eval_child, _ = self.__minimax(new_state, current_depth + 1)

            if is_max_turn and best_value < eval_child:
                best_value = eval_child
                action_target = action

            elif (not is_max_turn) and best_value > eval_child:
                best_value = eval_child
                action_target = action

        return best_value, action_target

    def eval(self, state):
        utility = 1 * (state.energy_self - state.energy_enemy)

        if state.energy_enemy <= 0:
            utility += 1000
        if state.energy_self <= 0:
            utility -= 1000

        angle_to_enemy = Action.angleTo(state.pos_self, state.pos_enemy, state.angle_self)
        state.self_faces_enemy = angle_to_enemy
        #print(f"Winkel zum Gegner: {angle_to_enemy}")
        utility -= 2 * angle_to_enemy
        angle_to_self = Action.angleTo(state.pos_enemy, state.pos_self, state.angle_enemy)
        state.enemy_faces_self = angle_to_self
        utility += angle_to_self

        if state.shot_possibly_by_enemy:
            utility -= 100
        if state.shot_possibly_at_enemy:
            utility += 100

        return self, utility


    def onHitWall(self):
        self.reset()  # To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event)
        self.rPrint('ouch! a wall !')

    def sensors(self):  # NECESARY FOR THE GAME
        pass

    def onRobotHit(self, robotId, robotName):  # when My bot hit another
        self.rPrint('collision with:' + str(robotId))

    def onHitByRobot(self, robotId, robotName):
        self.rPrint("damn a bot collided me!")

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower):  # NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.rPrint("hit by " + str(bulletBotId) + "with power:" + str(bulletPower))

    def onBulletHit(self, botId, bulletId):  # NECESARY FOR THE GAME
        """when my bullet hit a bot"""
        self.rPrint("fire done on " + str(botId))

    def onBulletMiss(self, bulletId):  # NECESARY FOR THE GAME
        """when my bullet hit a wall"""
        self.rPrint("the bullet " + str(bulletId) + " fail")

    def onRobotDeath(self):  # NECESARY FOR THE GAME
        """When my bot die"""
        self.rPrint("damn I'm Dead")

    def onTargetSpotted(self, botId, botName, botPos):  # NECESARY FOR THE GAME
        "when the bot see another one"
        self.fire(5)
        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos[0]) + " , y:" + str(botPos[1]))

    def onEnemyDeath(self):
        pass