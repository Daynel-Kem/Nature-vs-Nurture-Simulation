import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
import time
import threading
from agent import Agent, Task, clamp  # Import your existing code
from tasks import total_tasks
import numpy as np
import requests
# from analyzer import call_gemini

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pissbabypoopoo'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, resources={r"/analyzeagent": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}},
     supports_credentials=True)

HISTORY_WINDOW = 10
AI_SERVER = "http://0.0.0.0:8000/"

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
    simulation_state['agents'] = [Agent(i) for i in range(num_agents)]
    simulation_state['tasks'] = TASKS
    simulation_state['round'] = 0
    simulation_state['dropouts'] = []
    simulation_state['running'] = False
    
    for agent in simulation_state['agents']:
        agent.total_tasks_attempted = 0
        agent.total_tasks_succeeded = 0
        agent.task_difficulty_sum = 0
        agent.reward_history = []
        agent.initial_rewards = agent.rewards

        # NEW: rolling history buffer
        agent.history = []

def record_agent_history(agent, task, outcome):
    entry = {
        "round": simulation_state["round"],
        "age": agent.age,
        "task": task.name,
        "difficulty": task.difficulty,
        "success": outcome["success"],
        "reward": outcome["reward"],
        "loss": outcome["loss"],
        "confidence": float(agent.identity.confidence),
        "competence": float(agent.identity.competence),
        "aspiration": float(agent.identity.aspiration),
        "risk_tolerance": float(agent.identity.risk_tolerance),
        "money": float(agent.rewards)
    }

    agent.history.append(entry)

    # Keep only last N entries
    if len(agent.history) > HISTORY_WINDOW:
        agent.history.pop(0)

def run_simulation_round():
    agents = simulation_state['agents']
    tasks = simulation_state['tasks']
    
    print(f"Running round {simulation_state['round']} with {len(agents)} agents")
    
    for agent in agents:
        if not agent.alive:
            continue
            
        chosen_task = agent.choose_task(tasks)
        outcome = chosen_task.is_success(agent)

        # NEW: record history
        record_agent_history(agent, chosen_task, outcome)
        
        # Existing tracking
        agent.total_tasks_attempted += 1
        if outcome['success']:
            agent.total_tasks_succeeded += 1
        agent.task_difficulty_sum += chosen_task.difficulty
        agent.reward_history.append(agent.rewards)
        
        agent.update(outcome)
        agent.interact(agents)
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
            "gender": agent.gender,  # ADD THIS LINE
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
            
            # Agent history for trajectory graph - ADD THIS LINE
            "history": agent.history if hasattr(agent, 'history') else []
        }
        
        agent_list.append(agent_data)
    
    return agent_list

def summarize_agent_for_llm(agent):
    """
    Produces a compact, narrative-ready summary of an agent's recent life trajectory.
    Intended for private LLM analysis (Gemini).
    """

    history = agent.history
    if not history:
        return {
            "summary": "No meaningful history yet.",
            "signals": {
                "trajectory": "unknown",
                "most_common_task": "unknown",
                "pressure": "unknown",
                "alive": agent.alive
            }
        }

    successes = sum(1 for h in history if h["success"])
    failures = len(history) - successes

    avg_difficulty = sum(h["difficulty"] for h in history) / len(history)
    avg_confidence = sum(h["confidence"] for h in history) / len(history)
    avg_competence = sum(h["competence"] for h in history) / len(history)

    reward_delta = history[-1]["money"] - history[0]["money"]

    repeated_tasks = {}
    for h in history:
        repeated_tasks[h["task"]] = repeated_tasks.get(h["task"], 0) + 1
    most_common_task = max(repeated_tasks, key=repeated_tasks.get)

    trajectory = (
        "improving" if successes > failures
        else "declining" if failures > successes
        else "stagnant"
    )

    pressure = "high" if agent.wealth == "Low" else "moderate" if agent.wealth == "Middle" else "low"

    summary_text = (
        f"The agent comes from a {agent.wealth.lower()}-wealth background and has recently "
        f"experienced a {trajectory} trajectory. Over the last {len(history)} periods, "
        f"they succeeded {successes} times and failed {failures} times, most often engaging in "
        f"'{most_common_task}', a task of roughly {avg_difficulty:.2f} difficulty. "
        f"Their confidence averages around {avg_confidence:.2f}, while competence sits near "
        f"{avg_competence:.2f}. Financially, their situation has "
        f"{'improved' if reward_delta > 0 else 'worsened' if reward_delta < 0 else 'remained stable'}. "
        f"The environment exerts {pressure} pressure on their decisions."
    )

    return {
        "summary": summary_text,
        "signals": {
            "trajectory": trajectory,
            "successes": successes,
            "failures": failures,
            "avg_difficulty": avg_difficulty,
            "avg_confidence": avg_confidence,
            "avg_competence": avg_competence,
            "reward_delta": reward_delta,
            "most_common_task": most_common_task,
            "pressure": pressure,
            "alive": agent.alive
        }
    }

def build_prompt(summary_payload):
    summary = summary_payload["summary"]
    signals = summary_payload["signals"]

    return f"""
        You are analyzing a single simulated agent in a controlled social experiment.
        This analysis is private and visible only to the user.

        The following summary is complete and accurate. Do NOT introduce new events,
        tasks, relationships, or numerical values beyond what is implied here.

        AGENT SUMMARY:
        {summary}

        STRUCTURAL SIGNALS:
        - Life trajectory: {signals['trajectory']}
        - Dominant task pattern: {signals['most_common_task']}
        - Environmental pressure level: {signals['pressure']}
        - Current survival status: {"alive" if signals['alive'] else "no longer active"}

        TASK:
        Write a short interpretive reflection (4–6 sentences) explaining what may have
        happened during this period to shape the agent’s behavior and mindset.

        GUIDELINES:
        - Focus on structural constraints, repeated exposure, adaptation, and psychological response
        - Frame outcomes as plausible interpretations, not certainties
        - Avoid statistics, equations, or technical language
        - Do NOT invent specific life events (e.g., illness, family, education)
        - Do NOT mention that this is a simulation or that the agent is artificial
        - Maintain a neutral, analytical tone (not moralizing, not motivational)

        The goal is to help the reader understand how patterns of opportunity,
        pressure, and repetition may have influenced this individual’s trajectory.
        """



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
        },
        'avgCompetence': {
            'Low': 0,
            'Middle': 0,
            'High': 0
        },
        'avgAspiration': {
            'Low': 0,
            'Middle': 0,
            'High': 0
        },
        'avgRiskTolerance': {
            'Low': 0,
            'Middle': 0,
            'High': 0
        },
        'avgMoney': {
            'Low': 0,
            'Middle': 0,
            'High': 0
        }
    }
    
    # Calculate averages by class
    for wealth_class in ['Low', 'Middle', 'High']:
        class_agents = [a for a in alive_agents if a.wealth == wealth_class]
        if class_agents:
            # Confidence
            avg_conf = sum(a.identity.confidence for a in class_agents) / len(class_agents)
            stats['avgConfidence'][wealth_class] = float(avg_conf)
            
            # Competence
            avg_comp = sum(a.identity.competence for a in class_agents) / len(class_agents)
            stats['avgCompetence'][wealth_class] = float(avg_comp)
            
            # Aspiration
            avg_asp = sum(a.identity.aspiration for a in class_agents) / len(class_agents)
            stats['avgAspiration'][wealth_class] = float(avg_asp)
            
            # Risk Tolerance
            avg_risk = sum(a.identity.risk_tolerance for a in class_agents) / len(class_agents)
            stats['avgRiskTolerance'][wealth_class] = float(avg_risk)
            
            # Money
            avg_money = sum(a.rewards for a in class_agents) / len(class_agents)
            stats['avgMoney'][wealth_class] = float(avg_money)
    
    return stats


def find_agent_by_id(agent_id: int):
    for a in simulation_state['agents']:
        if a.id == agent_id:
            return a
    return None



@app.route('/')
def index():
    return "Nature vs Nurture Simulation Server Running"


@app.route("/analyzeagent", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:3000","http://127.0.0.1:3000"],
              supports_credentials=False,
              methods=["POST","OPTIONS"],
              allow_headers=["Content-Type","Authorization"])
def analyze_agent():
    if request.method == 'OPTIONS':
        # Preflight request: tell browser it’s allowed
        return ('', 204)
    

    payload = request.get_json(silent=True) or {}
    agent_id = payload.get("agent_id")

    if agent_id is None:
        return jsonify({"error": "agent_id is required"}), 400

    agent = find_agent_by_id(agent_id)
    if agent is None:
        return jsonify({"error": f"Agent {agent_id} not found"}), 404

    summary = summarize_agent_for_llm(agent)
    prompt = build_prompt(summary)

    try:
        r = requests.post(f"{AI_SERVER}analyze", json={"prompt": prompt}, timeout=20)
        r.raise_for_status()
        response = r.json()
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502

    return jsonify({
        "agent_id": agent_id,
        "analysis": response["message"]
    })

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
    
    elif command == 'unpause':
        if not simulation_state['running']:
            simulation_state['running'] = True
            # Restart simulation loop in background thread
            thread = threading.Thread(target=simulation_loop)
            thread.daemon = True
            thread.start()
            emit('simulation_unpaused', {'message': 'Simulation resumed'})
    
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