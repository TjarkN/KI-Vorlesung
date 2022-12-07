#! /usr/bin/python
# -*- coding: utf-8 -*-
from AI.actions import Action
from Objects.robot import Robot  # Import a base Robot
from pyswip import Prolog
from math import pi
import datetime


class R2D2(Robot):  # Create a Robot


    def init(self):  # To initialyse your robot

        # Feel free to customize: Set the bot color in RGB
        self.setColor(0, 0, 100)
        self.setGunColor(0, 0, 100)
        self.setRadarColor(0, 60, 0)
        self.setBulletsColor(255, 150, 150)
        self.maxDepth = 5

        #Don't Change
        self.setRadarField("thin")
        self.radarVisible(True)  # if True the radar field is visible
        self.gun_to_side()
        self.lockRadar("gun")
        self.size = self.getMapSize()
        self.duration = 0
        self.count_moves = 0
        self.percetions = []

        #Creating Knowledge Base
        self.kb = Prolog()
        #load the static rules of a database
        self.kb.consult("r2d2.pl")
        #set static but game-depending facts
        if len(list(self.kb.query("fact(map_size(X))"))) == 0:
            self.kb.assertz("fact(map_size([{},{}]))".format(float(self.size[0]), float( self.size[1])))
            #set goals eg.
            #self.kb.assertz("goal(pos(self,[100,50]))")

    def __del__(self):
        print(str(self) + ": " + str(self.duration/self.count_moves))

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
            - turns 45° tu the right: self.turn_right()
            - turns 45° tu the left: self.turn_left()
            - move 50 points forward: self.forward()
            - move 50 points backward: self.backwards()
            - shoots cost 3 points of energy (when the enemy is hit he gets 9 points damage and you receive 6 points cure): self.shoot()
        """
        # Tell current Perception in KB
        pos_self = [self.getPosition().x(), self.getPosition().y()]
        if self.getPosition_enemy() != None:
            pos_enemy = [self.getPosition_enemy().x(), self.getPosition_enemy().y()]
        else:
            return

        # delete old percetions (e.g.)
        try:
            self.kb.retract("fluent(energy(self,_))")
            self.kb.retract("fluent(energy(enemy,_))")

        except:
            print("No perceptions so far!")

        #for percept in self.percetions:
        #    self.kb.retract(percept)
        self.percetions = []

        # add new percetions
        self.percetions.append("fluent(energy(self,{}))".format(self.energy_left_self()))
        self.percetions.append("fluent(energy(enemy,{}))".format(self.energy_left_enemy()))

        for percept in self.percetions:
            self.kb.assertz(percept)

        #to debug print the current Knowledge Base
        #print("===================STARTS HERE=================================================")
        #a = list(self.kb.query("listing"))

        #Ask for best action
        before = datetime.datetime.now()
        selected_key_action = self.choose_action()
        after = datetime.datetime.now()
        self.duration += (after - before).microseconds
        self.count_moves += 1

        #perform action (select the action based on the results of the inference
        #if selected_key_action == "turn_left self":
        #    self.turn_right()
        #elif selected_key_action == "turn_right self":
        #    self.turn_left()

    def choose_action(self):
        #get the list of actions that lead to the definded goals
        try:
            selected_key_action = list(self.kb.query("time(once(a_star(S,P)))"))[0]["P"]
        except:
            selected_key_action = []
            print ("No answers from knowledge base")

        if len(selected_key_action) == 0:
            return ""
        else:
            key_action = selected_key_action[0].name.value
            for arg in selected_key_action[0].args:
                key_action += " " + arg.value
            return key_action

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
        # delete old percetions
        for percept in self.percetions:
            self.kb.retract(percept)
        self.percetions = []

    def onTargetSpotted(self, botId, botName, botPos):  # NECESARY FOR THE GAME
        "when the bot see another one"
        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos.x()) + " , y:" + str(botPos.y()))
