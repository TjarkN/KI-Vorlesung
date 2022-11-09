#! /usr/bin/python
# -*- coding: utf-8 -*-
from AI.actions import Action
from AI.state import State
from random import shuffle

from Objects.robot import Robot  # Import a base Robot


class MiniMaxAgent(Robot):  # Create a Robot


    def init(self):  # To initialyse your robot

        # Feel free to customize: Set the bot color in RGB
        self.setColor(0, 155, 187) # 197/0/132

        self.setGunColor(0, 155, 187)
        self.setRadarColor(0, 155, 187)
        self.setBulletsColor(0, 155, 187)
        self.maxDepth = 3

        #Don't Change
        self.setRadarField("thin")
        self.radarVisible(True)  # if True the radar field is visible
        self.gun_to_side()
        self.lockRadar("gun")
        size = self.getMapSize()

    def run(self):  # main loop to command the bot
        """
        to create your own bot, create an new python-file in python package "Robots" and giv it a name
        copy the code of simplebot and rename the class
        starting the main.py starts the game

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
        action = self.__minimax(state, current_depth=0)[1]
        possible_actions = state.get_possible_actions(enemy=False)
        if action == 'turn_left' or action == 'turn_right':
            self.turn(possible_actions[action])
        elif action == 'forward' or action == 'backward':
            self.move(possible_actions[action])
        else:
            self.fire(possible_actions[action])

    def __minimax(self, state, current_depth):

        if current_depth == self.maxDepth or state.is_terminal():
            eval = state.eval()[1]
            return eval, ""

        is_max_turn = True if current_depth % 2 == 0 else False
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
        """implement your evaluation function here"""
        utility = 0
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
        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos.x()) + " , y:" + str(botPos.y()))

    def onEnemyDeath(self):
        pass