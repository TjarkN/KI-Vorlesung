import numpy as np
from AI.game_environment import GameEnvironment
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adam
from keras.layers import Dropout, BatchNormalization
from keras import regularizers
from AI.actions import Action


class Training:

    def __init__(self, x, y, botList, no_graphics = True):
        # parameters
        max_memory = 5000  # Maximum number of experiences we are storing Standard 500
        hidden_size = 100  # Size of the hidden layers
        num_inputvars = 7
        #num_inputvars = 10
        self.batch_size = 20# Number of experiences we use for training per batch Standard 10
        self.epochs_left = 4000 # Number of games played in training, I found the model needs about 4,000 games till it plays well
        self.epsilon = 0.5/self.epochs_left  # exploration
        self.min_epsilon = 0.1
        self.matches_per_Game = 10
        self.matches_left = self.matches_per_Game
        self.frq_update_target_model = 10# update target model every x epochs
        self.start_training = self.epochs_left-10 #starting training after x epochs_left

        self.frequency_training = 1 #Training only started every x calls
        self.training_count = 0 #Amounts of trainings called by agent

        # Reseting the win counter
        self.win_cnt = 0
        # We want to keep track of the progress of the AI over time, so we save its win count history
        self.win_hist = []
        self.loss = .0
        self.loss_hist = []

        num_actions = len(Action.get_actions())
        self.width = x
        self.height = y
        self.botList = botList

        # Initialize experience replay object
        self.exp_replay = ExperienceReplay(max_memory=max_memory)

        # Define model
        self.online_model = self.baseline_model(num_inputvars, num_actions, hidden_size)
        self.target_model = self.baseline_model(num_inputvars, num_actions, hidden_size)
        self.update_target_model()
        # self.model.summary()

        #self.rl_bot = None
        self.env = GameEnvironment(self.width, self.height, no_grafics = no_graphics)
        self.reset_game(True)

    def save_model(self):
        # serialize model to JSON
        model_json = self.online_model.to_json()
        with open("model_RLBot.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.online_model.save_weights("model_RLBot.h5")

    def training_done(self):
        print("Training done")
        self.save_model()
        plt.close()
        plt.plot(self.moving_average_diff(self.win_hist, int(len(self.win_hist) / 100)))
        plt.ylabel('Average of victories per game')
        plt.show(1)
        plt.plot(self.loss_hist)
        plt.ylabel('Training loss per game')
        plt.show(1)

    def train(self, input_t0 = None, action = None, input_t1 = None, reward = None, game_over = False):
        # Train
        # Epochs is the number of games we play
        self.training_count += 1

        if reward == 1:
            self.win_cnt += 1

        # store experience
        self.exp_replay.remember([input_t0, action, reward, input_t1], game_over)

        #self.exp_replay.remember_TD([input_t0, action, reward, input_t1], game_over, self.online_model, self.target_model)

        if game_over:
            self.matches_left -= 1
            if self.matches_left == 0:
                self.epochs_left -= 1
                print("epochs left:" + str(self.epochs_left)+" win count: "+str(self.win_cnt)+" loss: "+str(self.loss))
                # Resetting the game
                self.win_hist.append(self.win_cnt)
                self.win_cnt = 0
                self.loss_hist.append(self.loss)
                self.loss = .0
                self.matches_left = self.matches_per_Game
                if self.epochs_left % self.frq_update_target_model == 0:
                    self.update_target_model()
                if self.epochs_left == 0:
                    self.training_done()
                    return
            self.reset_game(False)
            return

        """
        The experiences < s, a, r, s’ > we make during gameplay are our training data.
        Here we first save the last experience, and then load a batch of experiences to train our model
        """
        if self.epochs_left > self.start_training:
            return

        if self.training_count % self.frequency_training == 0:
            #Update the TDs before Training
            #self.exp_replay.update_TDs(self.online_model, self.target_model)

            # Load batch of experiences
            inputs, targets = self.exp_replay.get_batch(self.online_model, self.target_model, batch_size=self.batch_size)

            # train model on experiences
            batch_loss = self.online_model.train_on_batch(inputs, targets)

            # print(loss)
            self.loss += batch_loss

    def reset_game(self, first_time=False):
        botList = []
        models = []
        trainings = []
        for bot in self.botList:
            botList.append(bot[0])
            if bot[1]:
                models.append(self.online_model)
                trainings.append(self)
            else:
                models.append(None)
                trainings.append(None)
        #self.win_cnt = 0

        if first_time:
            self.env.start(botList, models, trainings)
        else:
            self.env.restart(botList, models, trainings)


    def baseline_model(self, grid_size, num_actions, hidden_size):
        # setting up the model with keras
        model = Sequential()
        model.add(Dense(hidden_size, input_shape=(grid_size,), activation='relu' ,kernel_regularizer=regularizers.l2(0.0001)))
        #model.add(BatchNormalization())
        model.add(Dense(hidden_size, activation='relu' ,kernel_regularizer=regularizers.l2(0.0001)))
        #model.add(BatchNormalization())
        model.add(Dense(hidden_size, activation='relu', kernel_regularizer=regularizers.l2(0.0001)))
        #model.add(BatchNormalization())
        model.add(Dense(hidden_size, activation='relu', kernel_regularizer=regularizers.l2(0.0001)))
        #model.add(BatchNormalization())
        model.add(Dense(num_actions, activation="sigmoid"))
        #model.compile(sgd(lr=.1), "mse")
        model.compile(Adam(), loss="mse")
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.online_model.get_weights())
        #self.exp_replay.update_TDs(self.online_model, self.target_model)


    def moving_average_diff(self, a, n=100):
        n = max(1, n)
        #diff = np.diff(a)
        diff = a
        ret = np.zeros(len(diff) - n, dtype=float)
        for i in range(len(diff) - n):
            ret[i] = sum(diff[i:i + n]) / n
        return ret

class ExperienceReplay(object):
    """
    During gameplay all the experiences < s, a, r, s’ > are stored in a replay memory.
    In training, batches of randomly drawn experiences are used to generate the input and target for training.
    """

    def __init__(self, max_memory=100, discount=.9):
        """
        Setup
        max_memory: the maximum number of experiences we want to store
        memory: a list of experiences
        discount: the discount factor for future experience

        In the memory the information whether the game ended at the state is stored seperately in a nested array
        [...
        [experience, game_over]
        [experience, game_over]
        ...]
        """
        self.max_memory = max_memory
        self.memory = []
        self.memory_TDs = []
        self.memory_Q_sas = []
        self.memory_targets =[]
        self.discount = discount

    def remember(self, states, game_over):
        # Save a state to memory
        self.memory.append([states, game_over])
        # We don't want to store infinite memories, so if we have too many, we just delete the oldest one
        if len(self.memory) > self.max_memory:
            del self.memory[0]

    def remember_TD(self, states, game_over, online_model, target_model):
        # Save a state to memory
        self.memory.append([states, game_over])

        #calculate and store TDs for memory
        target = online_model.predict(states[0])[0]
        Q_sa = states[2] + self.discount * np.max(target_model.predict(states[3])[0])
        TD = abs(Q_sa - target[states[1]])
        self.memory_TDs.append(TD)
        self.memory_Q_sas.append(Q_sa)
        self.memory_targets.append(target)

        # We don't want to store infinite memories, so if we have too many, we just delete the oldest one
        if len(self.memory) > self.max_memory:
            del self.memory[0]
            del self.memory_TDs[0]
            del self.memory_Q_sas[0]
            del self.memory_targets[0]

    def get_batch(self, online_model, target_model, batch_size=10):

        # How many experiences do we have?
        len_memory = len(self.memory)

        # Calculate the number of actions that can possibly be taken in the game
        num_actions = online_model.output_shape[-1]

        # Dimensions of the game field
        env_dim = self.memory[0][0][0].shape[1]

        # We want to return an input and target vector with inputs from an observed state...
        inputs = np.zeros((min(len_memory, batch_size), env_dim))

        # ...and the target r + gamma * max Q(s’,a’)
        # Note that our target is a matrix, with possible fields not only for the action taken but also
        # for the other possible actions. The actions do not take the same value as the prediction to not affect them
        targets = np.zeros((inputs.shape[0], num_actions))

        # We draw states to learn from randomly
        #We draw states proportianaly to their temporal differenz (TD)
        for i, idx in enumerate(np.random.randint(0, len_memory,
                                                  size=inputs.shape[0])):
            """
            Here we load one transition <s, a, r, s’> from memory
            state_t: initial state s
            action_t: action taken a
            reward_t: reward earned r
            state_tp1: the state that followed s’
            """
            state_t, action_t, reward_t, state_tp1 = self.memory[idx][0]

            # We also need to know whether the game ended at this state
            game_over = self.memory[idx][1]

            # add the state s to the input
            inputs[i:i + 1] = state_t

            # First we fill the target values with the predictions of the model.
            # They will not be affected by training (since the training loss for them is 0)
            targets[i] = online_model(state_t).numpy()[0]

            """
            If the game ended, the expected reward Q(s,a) should be the final reward r.
            Otherwise the target value is r + gamma * max Q(s’,a’)
            """
            #  Here Q_sa is max_a'Q(s', a') // bootstrapping use target model (Double Q-Learning)
            Q_sa = np.max(target_model(state_tp1).numpy()[0])

            # if the game ended, the reward is the final reward
            if game_over:  # if game_over is True
                targets[i, action_t] = reward_t
            else:
                # r + gamma * max Q(s’,a’)
                targets[i, action_t] = reward_t + self.discount * Q_sa
        return inputs, targets

    def get_batch_TD(self, online_model, target_model, batch_size=10):
        """
        Version for Prioritized Replay
        "draw states proportionally to their temporal difference (TD)"
        :param model:
        :param batch_size:
        :return:inputs, targets
        """

        # How many experiences do we have?
        len_memory = len(self.memory)

        # Calculate the number of actions that can possibly be taken in the game
        num_actions = online_model.output_shape[-1]

        # Dimensions of the game field
        env_dim = self.memory[0][0][0].shape[1]

        # We want to return an input and target vector with inputs from an observed state...
        inputs = np.zeros((min(len_memory, batch_size), env_dim))

        # ...and the target r + gamma * max Q(s’,a’)
        # Note that our target is a matrix, with possible fields not only for the action taken but also
        # for the other possible actions. The actions do not take the same value as the prediction to not affect them
        targets = np.zeros((inputs.shape[0], num_actions))


        # We draw states proportionally to their temporal difference (TD)
        sorted_TDs = np.array(self.memory_TDs,dtype='float64')
        sorted_TDs /= np.sum(sorted_TDs)

        batch_indexies = np.random.choice(len(self.memory), size = inputs.shape[0], replace=False, p = sorted_TDs)

        for i,idx in enumerate(batch_indexies):
            """
            Here we load one transition <s, a, r, s’> from memory
            state_t: initial state s
            action_t: action taken a
            reward_t: reward earned r
            state_tp1: the state that followed s’
            """
            m = self.memory[idx]
            state_t, action_t, reward_t, state_tp1 = m[0]

            # We also need to know whether the game ended at this state
            game_over = m[1]

            # add the state s to the input
            inputs[i:i + 1] = self.memory_targets[idx][action_t]

            # First we fill the target values with the predictions of the model.
            # They will not be affected by training (since the training loss for them is 0)
            targets[i] = online_model.predict(state_t).numpy()[0]#self.memory_targets[idx]

            """
            If the game ended, the expected reward Q(s,a) should be the final reward r.
            Otherwise the target value is r + gamma * max Q(s’,a’)
            """

            # if the game ended, the reward is the final reward
            if game_over:  # if game_over is True
                targets[i, action_t] = reward_t
            else:
                # r + gamma * max Q(s’,a’)
                targets[i, action_t] = self.memory_Q_sas[idx]
        return inputs, targets

    def update_TDs(self, online_model, target_model):
        #Calculatre the TD for each value in the memory
        for idx, m in enumerate(self.memory):
            state_t, action_t, reward_t, state_tp1 = m[0]
            target = online_model.predict(state_t)[0]
            Q_sa = reward_t + self.discount * np.max(target_model.predict(state_tp1).numpy()[0])
            TD = abs(Q_sa - target[action_t])
            self.memory_TDs[idx] = TD
            self.memory_Q_sas[idx] = Q_sa
            self.memory_targets[idx] = target

#rlbot_training = Training()
