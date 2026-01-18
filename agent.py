import random
import numpy as np
from enum import Enum
import names

DECAY_RATE = 40
AGE_HALF_LIFE = 40

class WEALTH_RATE(Enum):
    LOW = 0.7
    MIDDLE = 1
    HIGH = 1.6

class ADJUSTMENT_FACTOR(Enum):
    LOW = 1.3
    MIDDLE = 1
    HIGH = 0.5

Wealth_Rate = {
    "Low": 0.7,
    "Middle": 1,
    "High": 1.6
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
        self.gender = "male" if random.random() > 0.5 else "female"
        self.name = names.get_full_name(gender=self.gender)
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
        self.dropout_pressure = 0.0
        # your coolness factor (how likely you are to interact with other people)
        self.social_capital = random.uniform(0.1, 0.3) if self.wealth == "Low" else \
                      random.uniform(0.3, 0.6) if self.wealth == "Middle" else \
                      random.uniform(0.6, 0.9)


    def available_tasks(self, tasks):
        """
        Returns the list of tasks the agent can attempt.
        - Low-class agents can attempt most tasks, with occasional access to higher-class tasks.
        - Broke check relaxed for low-class to allow gambling their way up.
        - High-class still protected by overconfidence rules elsewhere.
        """
        available = []
        for task in tasks:
            # Capital requirement
            if task.required_capital and task.required_capital > self.rewards:
                # Low-class agents allowed to attempt low/mid-reward tasks even if undercapitalized
                if self.wealth != "Low" or task.reward > 20:
                    continue

            # Class requirement
            if task.required_class and self.wealth != task.required_class:
                # Rare chance for Low-class to breach class requirement
                if self.wealth == "Low" and random.random() < 0.05:
                    pass  # allow it
                else:
                    continue

            # Broke check
            # Low-class can attempt tasks even if it takes them slightly negative
            if self.wealth != "Low" and self.rewards < task.base_loss:
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

            # Overconfidence check
            if self.wealth == "High" and task.difficulty > self.identity.competence + 0.2:
                continue

            viable_tasks.append(task)

        # Final boss of every CS student
        if viable_tasks == []:
            return Task(
                name="Unemployment",
                difficulty=0.9,
                reward=0,
                variance=0,
                base_loss=15,
                repeatability=999
            )

        
        # elites be like ima do dat task anyway (low volatility, high long term reward)
        def task_score(task):
            expected_gain = task.reward * self.performance_estimate
            expected_loss = task.base_loss * (1 - self.performance_estimate)
            return expected_gain - expected_loss

        return max(viable_tasks, key=task_score)
    
    # the low confidence people bring each other down, opposite for high
    def peer_confidence_update(self, peer):
        delta = 0.02 * (peer.identity.confidence - self.identity.confidence)
        self.identity.confidence += delta
        self.identity.confidence = clamp(self.identity.confidence, 0, 1)

    def peer_opportunity(self, peer):
        if peer.wealth in ["Middle", "High"] and self.wealth == "Low":
            if random.random() < 0.05 * peer.social_capital:
                self.identity.aspiration += 0.1
                self.identity.aspiration = clamp(self.identity.aspiration, 0, 1)
                self.social_capital += 0.05
                self.social_capital = clamp(self.social_capital, 0, 1)

    def peer_learning(self, peer):
        # Only learn if peer is doing better
        if peer.identity.competence > self.identity.competence:
            # Only attempt learning if agent succeeded last task
            if self.last_task_succeeded and random.random() < 0.15:
                self.identity.competence += 0.02
                # Clamp so competence doesn't exceed max
                self.identity.competence = clamp(self.identity.competence, 0, 1)


    def interact(self, population):
        def pick_peers(agent, population, k=2):
            same = [a for a in population if a.wealth == agent.wealth and a.alive]
            above = [a for a in population if a.wealth > agent.wealth and a.alive]
            below = [a for a in population if a.wealth < agent.wealth and a.alive]

            peers = []
            if same:
                peers += random.sample(same, min(1, len(same)))
            if above and random.random() < 0.25:
                peers += random.sample(above, 1)
            if below and random.random() < 0.1:
                peers += random.sample(below, 1)
            return peers[:k]
    
        peers = pick_peers(self, population)
        for peer in peers:
            self.peer_confidence_update(peer)
            self.peer_opportunity(peer)
            self.peer_learning(peer)

    def update(self, outcome):
        # Youth buffers burnout (early coping)
        if self.age < 30:
            self.dropout_pressure *= 0.88
        elif self.age < 40:
            self.dropout_pressure *= 0.93
        else:
            self.dropout_pressure *= 0.97

        age_rate = np.exp(-self.age / DECAY_RATE) # updates become less drastic the older an agent is
        
       # social capital wears off over time
        self.social_capital *= 0.995

        # if ur trolling too much, you get downgraded
        if self.age > 50 and self.identity.confidence < 0.3:
            self.identity.aspiration *= 0.7
            self.identity.risk_tolerance *= 0.7

        observed = 1 if outcome["success"] else 0
        self.performance_estimate = (
            0.9 * self.performance_estimate + 0.1 * observed
        )

        if outcome["success"]:
            self.rewards += outcome["reward"] * Wealth_Rate[self.wealth]
            belief_delta = outcome["feedback"]
            confidence = clamp(self.identity.confidence, 0.2, 1)
            belief_delta *= confidence
            self.identity.confidence += 0.08 * Wealth_Rate[self.wealth]

            # NEW: success relieves dropout pressure
            self.dropout_pressure = max(0, self.dropout_pressure - 0.05)

            # Rare mentor boost, Senapi notices u
            if outcome["success"] and self.wealth == "Low":
                if random.random() < 0.08:
                    self.identity.competence += 0.05
                    self.identity.max_confidence += 0.1

        else:
            # You burn out and lose confidence when you're at rock bottom
            if self.wealth == "Low" and self.rewards < 10:
                self.rewards = 10
                self.identity.confidence -= 0.05
                self.identity.aspiration *= 0.9

            self.rewards -= outcome["loss"]
            belief_delta = outcome["feedback"]
            confidence = clamp(self.identity.confidence, 0.2, 1)
            belief_delta *= confidence

            # Failure hurts and persists
            scar = {
                "Low": 0.02,
                "Middle": 0.01,
                "High": 0.0003
            }[self.wealth]
            self.identity.max_confidence -= scar

            # NEW: failure increases accumulated dropout pressure
            self.dropout_pressure += {
                "Low": 0.08,
                "Middle": 0.04,
                "High": 0.015
            }[self.wealth]

        if self.wealth == "High":
            self.identity.confidence += belief_delta * age_rate * WEALTH_RATE.HIGH.value
        elif self.wealth == "Low":
            self.identity.confidence += belief_delta * age_rate * WEALTH_RATE.LOW.value
        else:
            self.identity.confidence += belief_delta * age_rate

        self.identity.risk_tolerance += age_rate * (0.05 if outcome["success"] else -0.1)
        aspiration_gain = age_rate * belief_delta * 0.5
        if self.wealth == "Low" and self.age < 35:
            aspiration_gain *= 0.4
        self.identity.aspiration += aspiration_gain


        # Aspirational agents should feel misaligned if they underperform their aspirations
        aspiration_gap = self.identity.aspiration - self.identity.confidence
        if aspiration_gap > 0.2 and self.age > 30:
            self.dropout_pressure += 0.02

        # Reality Check, you're only as good as how talented u are
        task_signal = 1.0 if outcome["success"] else 0.0
        learning_rate = 0.03 * age_rate * Wealth_Rate[self.wealth]
        self.identity.competence += learning_rate * (
            task_signal - self.identity.competence
        )

        # Calibrates confidence to competence, you cant run away with optimism
        self.identity.confidence += clamp(
            0.01 * age_rate * (
                self.identity.competence - self.identity.confidence
            ),
            -0.005,
            0.005
        )

        max_competence = 0.6 + 0.4 * self.talent
        self.identity.competence = min(self.identity.competence, max_competence)
        self.identity.confidence = clamp(
            self.identity.confidence,
            0.05,
            self.identity.max_confidence
        )
        low, high = RISK_BANDS[self.identity.risk_class]
        self.identity.risk_tolerance = clamp(self.identity.risk_tolerance, low, high)
        self.identity.aspiration = clamp(self.identity.aspiration, 0, 1)

        # Passive capital growth (rich gets richer baby, capitalism)
        capital_return = {
            "Low": 0.00,
            "Middle": 0.01,
            "High": 0.025
        }[self.wealth]
        self.rewards += self.rewards * capital_return

        # Living aint free buddy, time to pay up
        LIVING_COST = {
            "Low": 2,
            "Middle": 4,
            "High": 6
        }
        self.rewards -= LIVING_COST[self.wealth]

        # But the rich gets a jail out of free card baby
        ELITE_FLOOR = {
            "Low": -10,
            "Middle": 0,
            "High": 20
        }
        if self.rewards < ELITE_FLOOR[self.wealth]:
            self.rewards = ELITE_FLOOR[self.wealth]

        # The rich get richer? what about the poor again?
        if self.last_task == "Unemployment":
            self.identity.confidence -= 0.05
            self.identity.confidence = clamp(self.identity.confidence, 0, 1)
            self.identity.aspiration -= 0.02
            self.identity.aspiration = clamp(self.identity.aspiration, 0, 1)

            # NEW: unemployment compounds dropout pressure
            self.dropout_pressure += 0.05

        # yea the poor really get hurt bad by the system, diminishing return
        if self.wealth == "Low" and self.rewards > 150:
            self.rewards *= 0.98

        # NEW: middle/high class tend to "settle" instead of dropping out
        if self.wealth != "Low" and self.dropout_pressure > 0.6:
            self.identity.aspiration *= 0.85
            self.identity.risk_tolerance *= 0.85
            self.dropout_pressure *= 0.7

        # still got some support left guys
        if self.wealth == "Low" and self.age < 30:
            self.rewards += 2

        # Rare positive life shock (luck)
        if self.wealth == "Low" and random.random() < 0.015:
            windfall = random.uniform(20, 80)
            self.rewards += windfall
            self.identity.confidence += 0.1

        # Social credit still limited by class unfortun
        SOCIAL_CAP_MAX = {
            "Low": 0.6,
            "Middle": 0.8,
            "High": 1.0
        }
        self.social_capital = min(self.social_capital, SOCIAL_CAP_MAX[self.wealth])



        # probabilistic dropout instead of instant death
        RESILIENCE = {
            "Low": 1.0,
            "Middle": 0.7,
            "High": 0.4
        }[self.wealth]

        if self.dropout_pressure > 0.8:
            dropout_chance = clamp(
                (self.dropout_pressure - 0.6) * RESILIENCE,
                0,
                0.5
            )
            if random.random() < dropout_chance:
                self.alive = False


    def state_summary(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
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

        luck = random.gauss(0, 0.05)

        # Doing the actual task
        performance = (agent.talent + 
                       luck + 
                       random.uniform(-self.variance, self.variance) * class_noise[agent.wealth])

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