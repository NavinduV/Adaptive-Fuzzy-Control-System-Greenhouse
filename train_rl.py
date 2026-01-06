from stable_baselines3 import PPO
from rl_env import GreenhouseEnv

env = GreenhouseEnv()

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=5000)

model.save("fuzzy_rl_agent")
