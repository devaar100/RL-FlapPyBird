# Reinforcement Learning Flappy Bird Bot

This bot learns via Q-Learning with every move made 

![alt text](https://raw.githubusercontent.com/devaar100/RL-FlapPyBird/master/FlapPyBird/ScreenShot.png)

### Working
With every move made, the bird observes the state it was in, and the action it took. With regards to their outcomes, it punishes or rewards the state-action pairs. After playing the game numerous times, the bird is able to consistently obtain high scores.

A reinforcement learning algorithm called Q-learning is utilized. This project is heavily influenced by the very well documented work of [harvitronix](https://github.com/harvitronix/reinforcement-learning-car). I was able to implement the concepts learned on modified version of [FlapPyBird](https://github.com/sourabhv/FlapPyBird) by sourabhv.

The purpose of this project is to eventually use the learnings from the game to operate a real-life remote-control car, using distance sensors. This version of the code attempts to simulate the use of sensors to get us a step closer to being able to use this in the real world.
