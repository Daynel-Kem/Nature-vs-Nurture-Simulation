from loop import Simulation
from agent import Task
from tasks import total_tasks

n = 10
Game = Simulation(N=n, tasks=total_tasks, max_steps=50)

Game.step_N_times(300)
for i in range(n):
    Game.agent_log(i,type="self belief")

# for i in range(20):
#     Game.step()
#     print(Game.history[i][0])
