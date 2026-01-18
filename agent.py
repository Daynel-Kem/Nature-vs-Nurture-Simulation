import random
import numpy as np
from enum import Enum
import names

DECAY_RATE = 40
AGE_HALF_LIFE = 40

class WEALTH_RATE(Enum):
    LOW = 0.7
    MIDDLE = 1
    HIGH = 1.3

class ADJUSTMENT_FACTOR(Enum):
    LOW = 1.3
    MIDDLE = 1
    HIGH = 0.7

Wealth_Rate = {
    "Low": 0.7,
    "Middle": 1,
    "High": 1.3
}

RISK_BANDS = {
    "safe": (0.05, 0.35),
    "striver": (0.25, 0.6),
    "elite": (0.45, 0.85),
}

wealth_classes = ["Low", "Middle", "High"]
class_probability = [33, 34, 33]

risk_classes =["safe", "striver", "elite"]

class Identity:
    def __init__(self, wealth, talent):
        noise = np.random.normal(0, 0.1)
        aspiration = 0
        belief = 0
        risk = 0
        if wealth == "Low":
            aspiration = clamp(0.3 + noise, 0, 1)
            low_belief = np.random.normal(0, 0.05)
            belief = clamp(talent + low_belief, 0, 1) # ensure that no agent has a negative self belief (it breaks lol)
            risk_probability = [65, 30, 5]
            risk = random.choices(risk_classes, weights=risk_probability, k=1)[0]

        elif wealth == "Middle":
            aspiration = clamp(0.5 + noise, 0, 1)
            middle_belief = np.random.normal(0.15, 0.05)
            belief = clamp(talent + middle_belief, 0, 1)
            risk_probability = [30, 40, 30]
            risk = random.choices(risk_classes, weights=risk_probability, k=1)[0]

        elif wealth == "High":
            aspiration = clamp(0.8 + noise, 0, 1)
            high_belief = np.random.normal(0.3, 0.05)
            belief = clamp(talent + high_belief, 0, 1)
            risk_probability = [20, 40, 40]
            risk = random.choices(risk_classes, weights=risk_probability, k=1)[0]
        """
        Aspiration:     The measure for which tasks the agent even considers
                        "What am I aiming for?"
        Risk:           The measure of which task to go for
                        "Am I willing to take risks?"
        Competence:     The measure of how good the agent believes themselves to be
                        "How capabale am I objectively?"
        Confidence:     "Do I believe I can succeed right now?"
                        
        """
        self.aspiration = aspiration
        self.competence = belief
        self.confidence = clamp(self.competence + np.random.normal(0, 0.1), 0, 1)
        self.risk_class = risk

        MAX_CONFIDENCE_BY_CLASS = {
            "Low": 0.6,
            "Middle": 0.8,
            "High": 1.0
        }

        self.max_confidence = (
            MAX_CONFIDENCE_BY_CLASS[wealth]
            + np.random.normal(0, 0.05)
        )
        low, high = RISK_BANDS[risk]
        self.risk_tolerance = random.uniform(low, high)


class Agent:
    """
    Randomly creates an Agent born into a random (weighted) class and identity
    
    Talent: The true ability of an Agent. This value is unknown to the Agent
    Wealth: One of three classes (Low, Middle, High) that decides the amount of bias they face
    Age: How old an agent is. The older an agent becomes, the more rigid their decision making becomes
    Identity: The agent's perception of itself. This is the main deciding factor when making decisions
    """
    def __init__(self, id: int):
        self.name = names.get_full_name()
        self.talent = random.random()
        self.wealth = random.choices(wealth_classes, weights=class_probability, k=1)[0]
        self.age = 0
        self.identity = Identity(self.wealth, self.talent)
        self.performance_estimate = self.identity.confidence
        if self.wealth == "High":
            self.rewards = 100
        elif self.wealth == "Middle":
            self.rewards = 50
        else:
            self.rewards = 30 # arbitrary starting amount of money/reward per class

        self.id = id
        self.alive = True
        self.last_task = None
        self.last_task_succeeded = False
        self.tasks_done = {}
        self.history = []

    def available_tasks(self, tasks):
        available = []
        for task in tasks:
            if task.required_capital and task.required_capital > self.rewards:
                continue

            if task.required_class and self.wealth != task.required_class:
                continue

            available.append(task)
        return available

    def choose_task(self, tasks):
        viable_tasks = []
        for task in self.available_tasks(tasks):
            # Aspiration Check
            if task.difficulty > self.identity.aspiration and random.random() < 0.7:
                continue

            # Risk Check
            expected_gap = self.identity.confidence - task.difficulty
            if expected_gap < -self.identity.risk_tolerance:
                continue

            # I'm too old for this shiiii
            if self.age > 40 and task.difficulty < self.identity.aspiration - 0.2:
                continue

            # Broke Check
            if self.rewards < task.base_loss:
                continue

            viable_tasks.append(task)

        if viable_tasks == []:
            return Task("No Available Task", difficulty=1, reward=0, variance=0, base_loss=20, repeatability=1)
        
        return max(viable_tasks, key=lambda x : x.reward)

    def update(self, outcome):
        age_rate = np.exp(-self.age / DECAY_RATE) # updates become less drastic the older an agent is

        observed = 1 if outcome["success"] else 0
        self.performance_estimate = (
            0.9 * self.performance_estimate + 0.1 * observed
        )

        if outcome["success"]:
            self.rewards += outcome["reward"]
            belief_delta = outcome["feedback"]
            confidence = clamp(self.identity.confidence, 0.2, 1)
            belief_delta *= confidence
            self.identity.confidence += 0.08 * Wealth_Rate[self.wealth]

        else:
            if self.wealth == "Low" and self.rewards < 10:
                self.alive = False # drop out if ur too under
            self.rewards += outcome["loss"]
            belief_delta = outcome["feedback"]
            confidence = clamp(self.identity.confidence, 0.2, 1)
            belief_delta *= confidence

            # Failure hurts and persists
            scar = {
                "Low": 0.03,
                "Middle": 0.015,
                "High": 0.0005
            }[self.wealth]

            self.identity.max_confidence -= scar

        if self.wealth == "High":
            self.identity.confidence += belief_delta * age_rate * WEALTH_RATE.HIGH.value
        elif self.wealth == "Low":
            self.identity.confidence += belief_delta * age_rate * WEALTH_RATE.LOW.value
        else:
            self.identity.confidence += belief_delta * age_rate


        self.identity.risk_tolerance += age_rate * (0.05 if outcome["success"] else -0.1)
        self.identity.aspiration += age_rate * belief_delta * 0.5
        
        # Aspirational agents should feel misaligned if they underperform their aspirations
        aspiration_gap = self.identity.aspiration - self.identity.confidence
        if aspiration_gap > 0.2:
            self.identity.risk_tolerance += 0.02 * age_rate

        # Reality Check, you're only as good as how talented u are
        task_signal = 1.0 if outcome["success"] else 0.0

        learning_rate = 0.03 * age_rate * Wealth_Rate[self.wealth]

        self.identity.competence += learning_rate * (
            task_signal - self.identity.competence
        )

        # Calibrates confidence to competence, you cant run away with optimism
        self.identity.confidence += clamp(0.01 * age_rate * (
            self.identity.competence - self.identity.confidence), -0.005, 0.005)

        max_competence = 0.6 + 0.4 * self.talent
        self.identity.competence = min(self.identity.competence, max_competence)
        self.identity.confidence = clamp(self.identity.confidence, 0.05, self.identity.max_confidence)
        low, high = RISK_BANDS[self.identity.risk_class]
        self.identity.risk_tolerance = clamp(self.identity.risk_tolerance, low, high)
        self.identity.aspiration = clamp(self.identity.aspiration, 0, 1)

    def state_summary(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "class": self.wealth,
            "alive": self.alive,
            "talent": self.talent.item() if isinstance(self.talent, np.floating) else self.talent,
            "money": self.rewards.item() if isinstance(self.rewards, np.floating) else self.rewards,
            "confidence": self.identity.confidence.item() if isinstance(self.identity.confidence, np.floating) else self.identity.confidence,
            "competence": self.identity.competence.item() if isinstance(self.identity.competence, np.floating) else self.identity.competence,
            "aspiration": self.identity.aspiration.item() if isinstance(self.identity.aspiration, np.floating) else self.identity.aspiration,
            "risk tolerance": self.identity.risk_tolerance.item() if isinstance(self.identity.risk_tolerance, np.floating) else self.identity.risk_tolerance,
            "last task": self.last_task,
            "succeeded last task?": self.last_task_succeeded,
        }


class Task:
    def __init__(self, name, difficulty, reward, variance, base_loss, repeatability, required_capital=None, required_class=None):
        self.difficulty = difficulty
        self.reward = reward
        self.variance = variance
        self.base_loss = base_loss
        self.name = name
        self.repeatability = repeatability
        self.required_capital = required_capital
        self.required_class = required_class 

    def is_success(self, agent: Agent):
        self.add_task(agent)

        # Increased variability for lower classes
        class_noise = {
            "Low": 1.4,
            "Middle": 1,
            "High": 0.7
        }

        # Doing the actual task
        performance = agent.talent + random.uniform(-self.variance, self.variance) * class_noise[agent.wealth]

        # Effects of training slows down as you age
        task_value = self.reward * np.exp(-agent.tasks_done[self.name] / self.repeatability)
        age_penalty = np.exp(-agent.age / AGE_HALF_LIFE)
        effective_reward = task_value * age_penalty

        if performance > self.difficulty:
            #print(f"Agent {agent.id} ({agent.name}) has successfully performed {self.name}")
            agent.last_task = self.name
            agent.last_task_succeeded = True
            return {
                "success": True,
                "reward": effective_reward,
                "loss": 0,
                "feedback": self.compute_feedback(agent, True, performance) * age_penalty
            }
        else:
            #print(f"Agent {agent.id} ({agent.name}) has failed {self.name}")
            if agent.wealth == "High":
                adjustment_factor = ADJUSTMENT_FACTOR.HIGH.value
            elif agent.wealth == "Middle":
                adjustment_factor = ADJUSTMENT_FACTOR.MIDDLE.value
            else:
                adjustment_factor = ADJUSTMENT_FACTOR.LOW.value
            agent.last_task_succeeded = False
            return {
                "success": False,
                "reward": 0,
                "loss": self.base_loss * adjustment_factor,
                "feedback": self.compute_feedback(agent, False, performance) * age_penalty
            }
        
    def compute_feedback(self, agent: Agent, success, performance):
        expected = agent.identity.confidence
        raw = performance - expected

        if agent.wealth == "High":
            return raw * WEALTH_RATE.HIGH.value if success else raw * ADJUSTMENT_FACTOR.HIGH.value 
        elif agent.wealth == "Middle":
            return raw * WEALTH_RATE.MIDDLE.value if success else raw * ADJUSTMENT_FACTOR.MIDDLE.value 
        else:
            return raw * WEALTH_RATE.LOW.value if success else raw * ADJUSTMENT_FACTOR.LOW.value
        
    def add_task(self, agent: Agent):
        if self.name in agent.tasks_done:
            agent.tasks_done[self.name] += 1
        else:
            agent.tasks_done[self.name] = 1

def clamp(val, a, b):
    return max(min(b, val), a)