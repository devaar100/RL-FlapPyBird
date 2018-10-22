import sys
sys.path.insert(0, '/users/aarnavjindal/desktop/rl')
from FlapPyBird import flappy
import numpy as np
import random
import csv
from nn import LossHistory,neural_net
import os.path
import timeit

NUM_INPUT = 11
GAMMA = 1  # Forgetting.
LR = 0.7

def train_net(model, params):

    filename = params_to_filename(params)

    train_frames = 300000  # Number of frames to play.
    batchSize = params['batchSize']
    buffer = params['buffer']

    # Just stuff used below.
    t = 0
    replay = []  # stores tuples of (S, A, R, S').

    loss_log = []

    # Create a new game instance.
    game_state = flappy.Game()
    game_state.init_elements()

    # Get initial state by doing nothing and getting the state.
    state,_ = game_state.frame_step(0)

    # Run the frames.
    while t < train_frames:

        t += 1

        # Choose an action.
        qval = model.predict(np.array([state]))[0]
        action = (np.argmax(qval))  # best
        if t%500 == 0:
            print(qval)

        # Take action, observe new state and get our treat.
        new_state,reward = game_state.frame_step(action)
        if t%1000 == 0:
            print(t,action,state,reward)
            

        # Experience replay storage.
        replay.append((state, action, reward, new_state))

        # If we're done observing, start training.
        if t > batchSize:

            # If we've stored enough in our buffer, pop the oldest.
            if len(replay) > buffer:
                replay.pop(0)

            # Randomly sample our experience replay memory
            minibatch = random.sample(replay, batchSize)

            # Get training values.
            X_train, y_train = process_minibatch(minibatch, model)

            # Train the model on this batch.
            history = LossHistory()
            model.fit(
                X_train, y_train, batch_size=batchSize,
                nb_epoch=1, verbose=0, callbacks=[history]
            )
            loss_log.append(history.losses)

        # Update the starting state with S'.
        state = new_state
            
        if reward == -1000:
            game_state.init_elements()
            state,_ = game_state.frame_step(0)

        # Save the model every 2500 frames.
        if t % 25000 == 0:
            model.save_weights('results/saved-models/' + filename + '-' +
                               str(t) + '.h5',
                               overwrite=True)
            print("Saving model %s - %d" % (filename, t))
        
        if t%50000 == 0:
            # Log results after we're done all frames.
            log_results(filename, loss_log)


def log_results(filename, data_collect, loss_log):
    # Save the results to a file so we can graph it later.
    with open('results/sonar-frames/loss_data-' + filename + '.csv', 'w') as lf:
        wr = csv.writer(lf)
        for loss_item in loss_log:
            wr.writerow(loss_item)

def process_minibatch(minibatch, model):
    
    mb_len = len(minibatch)

    old_states = np.zeros(shape=(mb_len, NUM_INPUT))
    actions = np.zeros(shape=(mb_len,))
    rewards = np.zeros(shape=(mb_len,))
    new_states = np.zeros(shape=(mb_len, NUM_INPUT))
    
    for i, m in enumerate(minibatch):
        old_state_m, action_m, reward_m, new_state_m = m
        old_states[i, :] = old_state_m[:]
        actions[i] = action_m
        rewards[i] = reward_m
        new_states[i, :] = new_state_m[:]
    
    old_qvals = model.predict(old_states, batch_size=mb_len)
    new_qvals = model.predict(new_states, batch_size=mb_len)

    maxQs = np.max(new_qvals, axis=1)
    y = old_qvals
    non_term_inds = np.where(rewards != -1000)[0]
    term_inds = np.where(rewards == -1000)[0]
    
    y[non_term_inds, actions[non_term_inds].astype(int)] = (1-LR)*y[non_term_inds, actions[non_term_inds].astype(int)] + LR*(rewards[non_term_inds] + (GAMMA * maxQs[non_term_inds]))
    y[term_inds, actions[term_inds].astype(int)] = rewards[term_inds]

    X_train = old_states
    y_train = y
    return X_train, y_train


def params_to_filename(params):
    return str(params['nn'][0]) + '-' + str(params['nn'][1]) + '-' + \
            str(params['batchSize']) + '-' + str(params['buffer']) + '-' + 'ver'+str(params['ver'])
    

if __name__ == "__main__":
    nn_param = [256,256]
    params = {
        "batchSize": 512,
        "buffer": 50000,
        "nn": nn_param,
        "ver": 19
    }
    model = neural_net(NUM_INPUT, nn_param,'')
    train_net(model, params)