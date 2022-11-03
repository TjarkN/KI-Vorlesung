from AI.game_environment import GameEnvironment
from Robots.charlier import Charlier
x = 500
y = 700

#create a game envoironment for automated access
env = GameEnvironment(x, y)
botList = []
models = []
trainings = []

model = None #create a Keras model here that is connected to the robot attribute self.model
training = None #you can pass a Traning class here that is connected to the robot attribute self.training

#Here you add your own Bot
bot = ReinforcementLearningBot
botList.append(bot)
models.append(model)
trainings.append(training)

#enemy
bot = Charlier
botList.append(bot)
#for the enemy we don't need a model or training
models.append(None)
trainings.append(None)

#first time start
env.start(botList, models, trainings)
#restart of game
env.restart(botList, models, trainings)