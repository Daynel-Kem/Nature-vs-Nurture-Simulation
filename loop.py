from agent import Agent, Task
import matplotlib.pyplot as plt

class Simulation:
    def __init__(self, N: int, tasks: list[Task], max_steps: int = 50):
        agents = []
        for i in range(N):
            agents.append(Agent(id=i))
        self.agents = agents
        self.tasks = tasks
        self.max_steps = max_steps

        self.active = False
        self.time = 0
        self.history = []
        self.log_state()

    def step(self):
        for agent in self.agents:
            self.step_agent(agent)

        self.log_state()
        self.time += 1

    def step_agent(self, agent: Agent):
        if not agent.alive:
            return
        
        task = agent.choose_task(self.tasks)
        outcome = task.is_success(agent)
        agent.update(outcome)

        agent.age += 1
        if agent.rewards <= 0:
            agent.alive = False

    def step_N_times(self, N):
        for i in range(N):
            self.step()

    def log_state(self):
        snapshot = []
        for agent in self.agents:
            snapshot.append({
                "time": self.time
            } | agent.state_summary())
        self.history.append(snapshot)

    def agent_log(self, id, type):
        agent_log = []
        for i in range(len(self.history)):
            agent_log.append(self.history[i][id])
            print(self.history[i][id])

        if type == "self belief":
            plt.plot([i for i in range(len(self.history))], [x["confidence"] for x in agent_log], label="Confidence", color="blue")
            plt.plot([i for i in range(len(self.history))], [x["competence"] for x in agent_log], label="Competence", color="green")
            plt.plot([i for i in range(len(self.history))], [x["talent"] for x in agent_log], label="True Talent", color="red")
            plt.xlabel('Age')
            plt.text(70, 0.2, agent_log[0]["class"])
            plt.legend()
            plt.title('Confidence and Competence to Time')
            plt.xlim(0, 300)
            plt.ylim(0, 1)
            plt.show()

        return agent_log




    

