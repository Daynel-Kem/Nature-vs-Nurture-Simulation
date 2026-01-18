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

total_tasks = survival_tasks + training_tasks + status_tasks + trap_tasks

# Generatively Make New Tasks depending on recent information or smth idk. use ai
