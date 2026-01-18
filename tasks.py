from agent import Task
"""
Types of Tasks
1. Survival / Maintenance
   - Low reward, low loss
   - Keeps agents afloat
   - Little identity feedback

2. Skill-Building (Training)
   - Negative short-term reward
   - Increases future success probability
   - Strong belief effect only if repeated

3. Status / Lottery
   - Very high reward
   - Very high variance
   - Identity-sensitive

4. Exploitative / Trap
   - Looks good short-term
   - Damages long-term belief or wealth

5. Credential / Signaling Tasks
   - Low immediate payoff, unlocks future access, belief-sensitive

6. Network / Social Capital Tasks
   - Reward scales with confidence + class; compounding but subtle

7. Creative / Passion Projects
   - Identity-heavy, volatile, class-fragile

8. Institutional / Bureaucratic Paths
   - Slow, safe, class-filtered, low variance

9. Informal / Shadow Economy
   - High accessibility, hidden long-term damage

10. Health / Burnout Management
   - No money, but prevents collapse

"""

# 1
survival_tasks = [
    Task(
        name="Day Labor",
        difficulty=0.25,
        reward=6,
        variance=0.05,
        base_loss=2,
        repeatability=12
    ),
    Task(
        name="Retail Shift",
        difficulty=0.30,
        reward=7,
        variance=0.04,
        base_loss=2,
        repeatability=15
    ),
    Task(
        name="Food Delivery",
        difficulty=0.35,
        reward=8,
        variance=0.06,
        base_loss=3,
        repeatability=10
    ),
    Task(
        name="Warehouse Work",
        difficulty=0.40,
        reward=9,
        variance=0.05,
        base_loss=3,
        repeatability=14
    ),
]

# 2
training_tasks = [
    Task(
        name="Online Course",
        difficulty=0.45,
        reward=0,
        variance=0.03,
        base_loss=5,
        repeatability=25,
        required_capital=10
    ),
    Task(
        name="Apprenticeship",
        difficulty=0.50,
        reward=2,
        variance=0.04,
        base_loss=6,
        repeatability=30,
        required_capital=15
    ),
    Task(
        name="Practice Project",
        difficulty=0.55,
        reward=3,
        variance=0.05,
        base_loss=7,
        repeatability=35,
        required_capital=5
    ),
    Task(
        name="Night Classes",
        difficulty=0.60,
        reward=4,
        variance=0.04,
        base_loss=8,
        repeatability=40,
        required_capital=8
    ),
]

# 3
status_tasks = [
    Task(
        name="Startup Pitch",
        difficulty=0.65,
        reward=40,
        variance=0.25,
        base_loss=12,
        repeatability=3,
        required_capital=50,
        required_class="Middle"
    ),
    Task(
        name="Art Breakthrough",
        difficulty=0.70,
        reward=50,
        variance=0.30,
        base_loss=15,
        repeatability=2,
        required_capital=30,
        required_class="Middle"
    ),
    Task(
        name="Competitive Exam",
        difficulty=0.75,
        reward=60,
        variance=0.20,
        base_loss=18,
        repeatability=4,
        required_capital=25,
        required_class="Middle"
    ),
    Task(
        name="Market Speculation",
        difficulty=0.80,
        reward=80,
        variance=0.35,
        base_loss=25,
        repeatability=1,
        required_capital=100,
        required_class="High"
    ),
    Task(
    name="Private Equity Deal",
    difficulty=0.6,
    reward=80,
    variance=0.1,
    base_loss=10,
    repeatability=5,
    required_capital=200,
    required_class="High"
    ),
]

# 4
trap_tasks = [
    Task(
        name="Gig Overwork",
        difficulty=0.35,
        reward=12,
        variance=0.10,
        base_loss=6,
        repeatability=6
    ),
    Task(
        name="High-Interest Loan",
        difficulty=0.30,
        reward=15,
        variance=0.00,
        base_loss=20,
        repeatability=8,
        required_capital=0
    ),
    Task(
        name="Burnout Hustle",
        difficulty=0.45,
        reward=18,
        variance=0.15,
        base_loss=10,
        repeatability=5
    ),
    Task(
        name="Reputation Gamble",
        difficulty=0.55,
        reward=25,
        variance=0.20,
        base_loss=20,
        repeatability=2
    ),
]

# 5
credential_tasks = [
    Task(
        name="Certification Exam",
        difficulty=0.55,
        reward=5,
        variance=0.05,
        base_loss=10,
        repeatability=10,
        required_capital=20
    ),
    Task(
        name="Prestige Degree",
        difficulty=0.70,
        reward=15,
        variance=0.08,
        base_loss=20,
        repeatability=1,
        required_capital=80,
        required_class="Middle"
    ),
    Task(
        name="Elite Fellowship",
        difficulty=0.75,
        reward=20,
        variance=0.10,
        base_loss=25,
        repeatability=1,
        required_capital=100,
        required_class="High"
    ),
]

# 6
network_tasks = [
    Task(
        name="Local Networking Event",
        difficulty=0.40,
        reward=6,
        variance=0.05,
        base_loss=3,
        repeatability=20
    ),
    Task(
        name="Industry Mixer",
        difficulty=0.55,
        reward=12,
        variance=0.10,
        base_loss=6,
        repeatability=12,
        required_capital=15
    ),
    Task(
        name="Exclusive Retreat",
        difficulty=0.65,
        reward=25,
        variance=0.08,
        base_loss=8,
        repeatability=5,
        required_capital=60,
        required_class="High"
    ),
]

# 7
creative_tasks = [
    Task(
        name="Independent Game Dev",
        difficulty=0.60,
        reward=30,
        variance=0.30,
        base_loss=12,
        repeatability=3
    ),
    Task(
        name="Content Creation",
        difficulty=0.55,
        reward=25,
        variance=0.35,
        base_loss=10,
        repeatability=4
    ),
    Task(
        name="Novel Writing",
        difficulty=0.65,
        reward=45,
        variance=0.40,
        base_loss=15,
        repeatability=2
    ),
]

# 8
institutional_tasks = [
    Task(
        name="Civil Service Exam",
        difficulty=0.50,
        reward=18,
        variance=0.05,
        base_loss=6,
        repeatability=6
    ),
    Task(
        name="Corporate Ladder",
        difficulty=0.60,
        reward=22,
        variance=0.06,
        base_loss=7,
        repeatability=10,
        required_class="Middle"
    ),
    Task(
        name="Executive Track",
        difficulty=0.70,
        reward=35,
        variance=0.05,
        base_loss=8,
        repeatability=8,
        required_class="High"
    ),
]

# 9
informal_tasks = [
    Task(
        name="Cash-Only Side Hustle",
        difficulty=0.30,
        reward=10,
        variance=0.10,
        base_loss=4,
        repeatability=12
    ),
    Task(
        name="Grey Market Trading",
        difficulty=0.45,
        reward=20,
        variance=0.25,
        base_loss=15,
        repeatability=5
    ),
    Task(
        name="Illegal Arbitrage",
        difficulty=0.55,
        reward=35,
        variance=0.40,
        base_loss=30,
        repeatability=2
    ),
]

# 10
recovery_tasks = [
    Task(
        name="Rest & Recovery",
        difficulty=0.20,
        reward=0,
        variance=0.00,
        base_loss=1,
        repeatability=50
    ),
    Task(
        name="Therapy & Coaching",
        difficulty=0.35,
        reward=0,
        variance=0.00,
        base_loss=5,
        repeatability=20,
        required_capital=20
    ),
]


total_tasks = (
    survival_tasks + 
    training_tasks + 
    status_tasks + 
    trap_tasks + 
    credential_tasks + 
    network_tasks +
    creative_tasks +
    institutional_tasks +
    informal_tasks +
    recovery_tasks
)

# Generatively Make New Tasks depending on recent information or smth idk. use ai
