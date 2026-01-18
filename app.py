import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading
from agent import Agent, Task, clamp  # Import your existing code
from tasks import total_tasks
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pissbabypoopoo'
socketio = SocketIO(app, cors_allowed_origins="*")

# Simulation state
simulation_state = {
    'running': False,
    'agents': [],
    'tasks': [],
    'round': 0,
    'max_rounds': 50,
    'dropouts': []
}

# Define your tasks (adjust as needed)
TASKS = total_tasks

def initialize_simulation(num_agents=100):
    """Initialize agents and reset state"""
    simulation_state['agents'] = [Agent(i) for i in range(num_agents)]
    simulation_state['tasks'] = TASKS
    simulation_state['round'] = 0
    simulation_state['dropouts'] = []
    simulation_state['running'] = False
    
    # Initialize tracking for each agent
    for agent in simulation_state['agents']:
        agent.total_tasks_attempted = 0
        agent.total_tasks_succeeded = 0
        agent.task_difficulty_sum = 0
        agent.reward_history = []
        agent.initial_rewards = agent.rewards

def run_simulation_round():
    agents = simulation_state['agents']
    tasks = simulation_state['tasks']
    
    print(f"Running round {simulation_state['round']} with {len(agents)} agents")
    
    for agent in agents:
        if not agent.alive:
            continue
            
        chosen_task = agent.choose_task(tasks)
        outcome = chosen_task.is_success(agent)
        
        # Track metrics
        agent.total_tasks_attempted += 1
        if outcome['success']:
            agent.total_tasks_succeeded += 1
        agent.task_difficulty_sum += chosen_task.difficulty
        agent.reward_history.append(agent.rewards)
        
        agent.update(outcome)
        agent.age += 1
        
        if not agent.alive and agent not in simulation_state['dropouts']:
            simulation_state['dropouts'].append(agent)
    
    simulation_state['round'] += 1

def simulation_loop():
    print("Simulation loop started!")
    while simulation_state['running']:
        if simulation_state['round'] >= simulation_state['max_rounds']:
            simulation_state['running'] = False
            socketio.emit('simulation_complete', {'message': 'Simulation finished'})
            break
        
        run_simulation_round()
        
        agent_data = get_agent_data()
        print(f"Emitting agent_update with {len(agent_data)} agents")
        
        socketio.emit('agent_update', {
            'type': 'agent_update',
            'agents': agent_data
        })
        
        stats = calculate_stats()
        print(f"Stats: Round {stats['round']}, Alive: {stats['alive']}")
        
        socketio.emit('stats_update', {
            'type': 'stats_update',
            'stats': stats
        })
        
        socketio.sleep(0.5)

def get_agent_data():
    """Serialize agent data for frontend with additional metrics"""
    agent_list = []
    
    for agent in simulation_state['agents']:
        # Calculate additional metrics
        avg_task_difficulty = (
            agent.task_difficulty_sum / agent.total_tasks_attempted 
            if agent.total_tasks_attempted > 0 else 0
        )
        
        failure_rate = (
            (agent.total_tasks_attempted - agent.total_tasks_succeeded) / agent.total_tasks_attempted
            if agent.total_tasks_attempted > 0 else 0
        )
        
        # Calculate reward rate (rewards per round)
        reward_rate = (
            (agent.rewards - agent.initial_rewards) / max(agent.age, 1)
            if agent.age > 0 else 0
        )
        
        # Get most repeated task for task repeatability metric
        if agent.tasks_done:
            most_repeated_task = max(agent.tasks_done.items(), key=lambda x: x[1])
            task_repeatability = most_repeated_task[1]
        else:
            task_repeatability = 0
        
        agent_data = {
            "id": agent.id,
            "name": agent.name,
            "age": agent.age,
            "class": agent.wealth,
            "alive": agent.alive,
            "talent": agent.talent.item() if isinstance(agent.talent, np.floating) else agent.talent,
            "money": agent.rewards.item() if isinstance(agent.rewards, np.floating) else agent.rewards,
            "confidence": agent.identity.confidence.item() if isinstance(agent.identity.confidence, np.floating) else agent.identity.confidence,
            "competence": agent.identity.competence.item() if isinstance(agent.identity.competence, np.floating) else agent.identity.competence,
            "aspiration": agent.identity.aspiration.item() if isinstance(agent.identity.aspiration, np.floating) else agent.identity.aspiration,
            "risk tolerance": agent.identity.risk_tolerance.item() if isinstance(agent.identity.risk_tolerance, np.floating) else agent.identity.risk_tolerance,
            "last task": agent.last_task,
            "succeeded last task?": agent.last_task_succeeded,
            
            # New metrics
            "avg_task_difficulty": float(avg_task_difficulty),
            "failure_rate": float(failure_rate),
            "reward_rate": float(reward_rate),
            "task_repeatability": int(task_repeatability),
            "total_rewards": float(agent.rewards),
            "initial_rewards": float(agent.initial_rewards),
        }
        
        agent_list.append(agent_data)
    
    return agent_list

def calculate_stats():
    """Calculate statistics for the current round"""
    agents = simulation_state['agents']
    alive_agents = [a for a in agents if a.alive]
    
    stats = {
        'round': simulation_state['round'],
        'alive': len(alive_agents),
        'dropouts': len(simulation_state['dropouts']),
        'avgConfidence': {
            'Low': 0,
            'Middle': 0,
            'High': 0
        }
    }
    
    # Calculate average confidence by class
    for wealth_class in ['Low', 'Middle', 'High']:
        class_agents = [a for a in alive_agents if a.wealth == wealth_class]
        if class_agents:
            avg_conf = sum(a.identity.confidence for a in class_agents) / len(class_agents)
            stats['avgConfidence'][wealth_class] = float(avg_conf)
    
    return stats


@app.route('/')
def index():
    return "Social Mobility Simulation Server Running"

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to simulation server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    simulation_state['running'] = False

@socketio.on('message')
def handle_message(data):
    """Handle incoming WebSocket messages"""
    command = data.get('command')
    
    if command == 'start':
        params = data.get('params', {})
        num_agents = params.get('num_agents', 100)
        num_rounds = params.get('num_rounds', 50)
        
        # Validate inputs
        num_agents = max(1, min(500, int(num_agents)))  # Clamp between 1 and 500
        num_rounds = max(1, min(200, int(num_rounds)))  # Clamp between 1 and 200
        
        print(f"Starting simulation with {num_agents} agents and {num_rounds} rounds")
        
        # Initialize simulation
        initialize_simulation(num_agents)
        simulation_state['max_rounds'] = num_rounds
        simulation_state['running'] = True
        
        # Start simulation in background thread
        thread = threading.Thread(target=simulation_loop)
        thread.daemon = True
        thread.start()
        
        emit('simulation_started', {
            'message': f'Simulation started with {num_agents} agents for {num_rounds} rounds'
        })
    
    elif command == 'pause':
        simulation_state['running'] = False
        emit('simulation_paused', {'message': 'Simulation paused'})
    
    elif command == 'reset':
        simulation_state['running'] = False
        initialize_simulation()
        emit('simulation_reset', {'message': 'Simulation reset'})
    
    elif command == 'get_state':
        emit('agent_update', {
            'type': 'agent_update',
            'agents': get_agent_data()
        })
        emit('stats_update', {
            'type': 'stats_update',
            'stats': calculate_stats()
        })

if __name__ == '__main__':
    initialize_simulation()
    print("Starting simulation server on http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)