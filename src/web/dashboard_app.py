"""
AI Assistant / Chat Interface - Web Dashboard with Natural Language Queries
Replaces CLI with user-friendly web interface and conversational AI
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import re
from typing import Dict, List, Any
import sqlite3

app = Flask(__name__)

class TimetableAI:
    """
    Natural Language Interface for Timetable Queries
    """
    
    def __init__(self):
        self.load_schedule_data()
        self.setup_query_patterns()
    
    def load_schedule_data(self):
        """Load current schedule data."""
        try:
            with open('output/timetable.json', 'r') as f:
                self.schedule_data = json.load(f)
        except FileNotFoundError:
            self.schedule_data = {'schedule': [], 'metadata': {}}
    
    def setup_query_patterns(self):
        """Setup natural language query patterns."""
        self.query_patterns = {
            r"show (?:me )?(.+)'s schedule": self.get_faculty_schedule,
            r"when is (.+) class": self.get_course_schedule,
            r"what(?:'s| is) in room (.+)": self.get_room_schedule,
            r"(?:what|which) classes (?:are )?on (.+)": self.get_day_schedule,
            r"show (?:me )?(?:the )?schedule for (.+)": self.get_general_schedule,
            r"how many (.+) do we have": self.get_count_query,
            r"(?:what|which) rooms are (?:being )?used": self.get_used_rooms,
            r"who (?:is )?teaching (.+)": self.get_course_teacher,
            r"when (?:does|is) (.+) (?:teach|teaching)": self.get_faculty_times,
            r"(?:what|which) classes are at (.+)": self.get_time_classes,
            r"show (?:me )?(?:all )?conflicts": self.get_conflicts,
            r"(?:what|which) building has (.+)": self.get_building_info,
            r"show (?:me )?statistics": self.get_statistics,
            r"(?:what|how) (?:is )?performance": self.get_performance_metrics
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query and return response."""
        query = query.lower().strip()
        
        for pattern, handler in self.query_patterns.items():
            match = re.search(pattern, query)
            if match:
                try:
                    return handler(match.groups())
                except Exception as e:
                    return {
                        'success': False,
                        'message': f"Error processing query: {str(e)}",
                        'type': 'error'
                    }
        
        return {
            'success': False,
            'message': "I couldn't understand your query. Try asking about schedules, rooms, faculty, or courses.",
            'type': 'help',
            'suggestions': [
                "Show me Dr. Alice's schedule",
                "When is Data Structures class?",
                "What's in Room 101?",
                "Which classes are on Monday?",
                "Show me statistics"
            ]
        }
    
    def get_faculty_schedule(self, groups: tuple) -> Dict[str, Any]:
        """Get schedule for a specific faculty member."""
        faculty_name = groups[0]
        schedule = []
        
        for slot in self.schedule_data.get('schedule', []):
            if faculty_name.lower() in slot['faculty']['name'].lower():
                schedule.append({
                    'day': slot['day'],
                    'time': f"{slot['start_time']}-{slot['end_time']}",
                    'course': slot['course']['name'],
                    'room': slot['room']['name'],
                    'students': slot['students']['count']
                })
        
        if schedule:
            return {
                'success': True,
                'message': f"Here's {faculty_name}'s schedule:",
                'data': schedule,
                'type': 'schedule'
            }
        else:
            return {
                'success': False,
                'message': f"No schedule found for faculty member '{faculty_name}'",
                'type': 'not_found'
            }
    
    def get_course_schedule(self, groups: tuple) -> Dict[str, Any]:
        """Get schedule for a specific course."""
        course_name = groups[0]
        schedule = []
        
        for slot in self.schedule_data.get('schedule', []):
            if course_name.lower() in slot['course']['name'].lower() or course_name.lower() in slot['course']['code'].lower():
                schedule.append({
                    'day': slot['day'],
                    'time': f"{slot['start_time']}-{slot['end_time']}",
                    'faculty': slot['faculty']['name'],
                    'room': slot['room']['name'],
                    'students': slot['students']['count']
                })
        
        if schedule:
            return {
                'success': True,
                'message': f"Here's the schedule for {course_name}:",
                'data': schedule,
                'type': 'schedule'
            }
        else:
            return {
                'success': False,
                'message': f"No schedule found for course '{course_name}'",
                'type': 'not_found'
            }
    
    def get_room_schedule(self, groups: tuple) -> Dict[str, Any]:
        """Get schedule for a specific room."""
        room_name = groups[0]
        schedule = []
        
        for slot in self.schedule_data.get('schedule', []):
            if room_name.lower() in slot['room']['name'].lower() or room_name.lower() in slot['room']['id'].lower():
                schedule.append({
                    'day': slot['day'],
                    'time': f"{slot['start_time']}-{slot['end_time']}",
                    'course': slot['course']['name'],
                    'faculty': slot['faculty']['name'],
                    'students': slot['students']['count']
                })
        
        if schedule:
            room_info = next((slot['room'] for slot in self.schedule_data.get('schedule', []) 
                            if room_name.lower() in slot['room']['name'].lower()), None)
            
            return {
                'success': True,
                'message': f"Here's the schedule for {room_name}:",
                'data': schedule,
                'room_info': room_info,
                'type': 'room_schedule'
            }
        else:
            return {
                'success': False,
                'message': f"No schedule found for room '{room_name}'",
                'type': 'not_found'
            }
    
    def get_day_schedule(self, groups: tuple) -> Dict[str, Any]:
        """Get schedule for a specific day."""
        day = groups[0].upper()
        schedule = []
        
        for slot in self.schedule_data.get('schedule', []):
            if day in slot['day'] or slot['day'].startswith(day[:3].upper()):
                schedule.append({
                    'time': f"{slot['start_time']}-{slot['end_time']}",
                    'course': slot['course']['name'],
                    'faculty': slot['faculty']['name'],
                    'room': slot['room']['name'],
                    'students': slot['students']['count']
                })
        
        # Sort by time
        schedule.sort(key=lambda x: x['time'])
        
        if schedule:
            return {
                'success': True,
                'message': f"Here's the schedule for {day}:",
                'data': schedule,
                'type': 'day_schedule'
            }
        else:
            return {
                'success': False,
                'message': f"No classes found for {day}",
                'type': 'not_found'
            }
    
    def get_statistics(self, groups: tuple) -> Dict[str, Any]:
        """Get overall statistics."""
        schedule = self.schedule_data.get('schedule', [])
        metadata = self.schedule_data.get('metadata', {})
        
        # Calculate statistics
        total_classes = len(schedule)
        rooms_used = len(set(slot['room']['id'] for slot in schedule))
        faculty_involved = len(set(slot['faculty']['id'] for slot in schedule))
        
        # Daily distribution
        daily_dist = {}
        for slot in schedule:
            day = slot['day']
            daily_dist[day] = daily_dist.get(day, 0) + 1
        
        # Time distribution
        time_dist = {}
        for slot in schedule:
            time = slot['start_time']
            time_dist[time] = time_dist.get(time, 0) + 1
        
        stats = {
            'total_classes': total_classes,
            'rooms_used': rooms_used,
            'faculty_involved': faculty_involved,
            'utilization_rate': f"{(total_classes/35)*100:.1f}%",
            'daily_distribution': daily_dist,
            'time_distribution': time_dist,
            'conflicts': metadata.get('conflicts', 0)
        }
        
        return {
            'success': True,
            'message': "Here are the current statistics:",
            'data': stats,
            'type': 'statistics'
        }
    
    def get_performance_metrics(self, groups: tuple) -> Dict[str, Any]:
        """Get performance metrics."""
        try:
            fitness = self.schedule_data.get('fitness_scores', {})
            
            metrics = {
                'constraint_satisfaction': f"{100 if fitness.get('hard_violations', 1) == 0 else 0}%",
                'preference_score': f"{fitness.get('preference_score', 0):.1f}/10",
                'soft_penalty': fitness.get('soft_penalty', 0),
                'schedule_validity': 'Valid' if self.schedule_data.get('metadata', {}).get('is_valid') else 'Invalid'
            }
            
            return {
                'success': True,
                'message': "Here are the performance metrics:",
                'data': metrics,
                'type': 'performance'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error retrieving performance metrics: {str(e)}",
                'type': 'error'
            }

# Initialize AI assistant
ai_assistant = TimetableAI()

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/query', methods=['POST'])
def handle_query():
    """Handle natural language queries."""
    data = request.get_json()
    query = data.get('query', '')
    
    response = ai_assistant.process_query(query)
    return jsonify(response)

@app.route('/api/schedule')
def get_schedule():
    """Get current schedule data."""
    return jsonify(ai_assistant.schedule_data)

@app.route('/api/visualization/<viz_type>')
def get_visualization(viz_type):
    """Generate visualizations."""
    schedule = ai_assistant.schedule_data.get('schedule', [])
    
    if viz_type == 'daily_distribution':
        daily_counts = {}
        for slot in schedule:
            day = slot['day']
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        fig = go.Figure(data=[
            go.Bar(x=list(daily_counts.keys()), y=list(daily_counts.values()))
        ])
        fig.update_layout(title='Classes per Day')
        
    elif viz_type == 'room_utilization':
        room_counts = {}
        for slot in schedule:
            room = slot['room']['name']
            room_counts[room] = room_counts.get(room, 0) + 1
        
        fig = go.Figure(data=[
            go.Pie(labels=list(room_counts.keys()), values=list(room_counts.values()))
        ])
        fig.update_layout(title='Room Utilization')
        
    elif viz_type == 'time_distribution':
        time_counts = {}
        for slot in schedule:
            time = slot['start_time']
            time_counts[time] = time_counts.get(time, 0) + 1
        
        fig = go.Figure(data=[
            go.Bar(x=list(time_counts.keys()), y=list(time_counts.values()))
        ])
        fig.update_layout(title='Classes by Time Slot')
    
    else:
        return jsonify({'error': 'Unknown visualization type'})
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify({'graph': graphJSON})

# Create templates directory and HTML template
def create_dashboard_template():
    """Create the dashboard HTML template."""
    
    os.makedirs('templates', exist_ok=True)
    
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Timetable Scheduler Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            background-color: #f8f9fa;
        }
        .message {
            margin-bottom: 10px;
            padding: 8px 12px;
            border-radius: 8px;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            text-align: right;
        }
        .ai-message {
            background-color: #e9ecef;
            color: #333;
        }
        .visualization-container {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container-fluid mt-4">
        <h1 class="text-center mb-4">🎓 AI Timetable Scheduler Dashboard</h1>
        
        <div class="row">
            <!-- Chat Interface -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>💬 AI Assistant</h5>
                    </div>
                    <div class="card-body">
                        <div id="chat-container" class="chat-container"></div>
                        <div class="input-group mt-3">
                            <input type="text" id="query-input" class="form-control" 
                                   placeholder="Ask me about schedules, rooms, faculty..." 
                                   onkeypress="handleKeyPress(event)">
                            <button class="btn btn-primary" onclick="sendQuery()">Send</button>
                        </div>
                        <div class="mt-2">
                            <small class="text-muted">Try: "Show me Dr. Alice's schedule" or "What's in Room 101?"</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Quick Stats -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>📊 Quick Statistics</h5>
                    </div>
                    <div class="card-body" id="stats-container">
                        Loading statistics...
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Visualizations -->
        <div class="row mt-4">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h6>Daily Distribution</h6>
                    </div>
                    <div class="card-body">
                        <div id="daily-chart"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h6>Room Utilization</h6>
                    </div>
                    <div class="card-body">
                        <div id="room-chart"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h6>Time Distribution</h6>
                    </div>
                    <div class="card-body">
                        <div id="time-chart"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Schedule Table -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>📅 Current Schedule</h5>
                    </div>
                    <div class="card-body">
                        <div id="schedule-table"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let chatContainer = document.getElementById('chat-container');
        
        function addMessage(message, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
            messageDiv.innerHTML = message;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendQuery();
            }
        }
        
        async function sendQuery() {
            const input = document.getElementById('query-input');
            const query = input.value.trim();
            
            if (!query) return;
            
            addMessage(query, true);
            input.value = '';
            
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    let message = result.message;
                    
                    if (result.data) {
                        if (result.type === 'schedule') {
                            message += '<br><table class="table table-sm mt-2">';
                            message += '<tr><th>Day</th><th>Time</th><th>Course</th><th>Room</th></tr>';
                            result.data.forEach(item => {
                                message += `<tr><td>${item.day}</td><td>${item.time}</td><td>${item.course}</td><td>${item.room}</td></tr>`;
                            });
                            message += '</table>';
                        } else if (result.type === 'statistics') {
                            message += '<br><ul class="list-unstyled mt-2">';
                            for (const [key, value] of Object.entries(result.data)) {
                                if (typeof value === 'object') continue;
                                message += `<li><strong>${key.replace('_', ' ')}:</strong> ${value}</li>`;
                            }
                            message += '</ul>';
                        }
                    }
                    
                    addMessage(message);
                } else {
                    addMessage(`❌ ${result.message}`);
                    if (result.suggestions) {
                        result.suggestions.forEach(suggestion => {
                            addMessage(`💡 Try: "${suggestion}"`, false);
                        });
                    }
                }
            } catch (error) {
                addMessage('❌ Error processing query. Please try again.');
            }
        }
        
        async function loadVisualization(chartId, vizType) {
            try {
                const response = await fetch(`/api/visualization/${vizType}`);
                const result = await response.json();
                
                if (result.graph) {
                    Plotly.newPlot(chartId, JSON.parse(result.graph).data, JSON.parse(result.graph).layout);
                }
            } catch (error) {
                console.error('Error loading visualization:', error);
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: 'show me statistics' })
                });
                
                const result = await response.json();
                
                if (result.success && result.data) {
                    let html = '<div class="row">';
                    const stats = [
                        { label: 'Total Classes', value: result.data.total_classes, icon: '📚' },
                        { label: 'Rooms Used', value: result.data.rooms_used, icon: '🏫' },
                        { label: 'Faculty Involved', value: result.data.faculty_involved, icon: '👨‍🏫' },
                        { label: 'Utilization', value: result.data.utilization_rate, icon: '📊' }
                    ];
                    
                    stats.forEach(stat => {
                        html += `
                            <div class="col-md-6 mb-3">
                                <div class="d-flex align-items-center">
                                    <span class="fs-3 me-2">${stat.icon}</span>
                                    <div>
                                        <div class="fw-bold">${stat.value}</div>
                                        <small class="text-muted">${stat.label}</small>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    
                    document.getElementById('stats-container').innerHTML = html;
                }
            } catch (error) {
                document.getElementById('stats-container').innerHTML = '❌ Error loading statistics';
            }
        }
        
        // Initialize dashboard
        window.onload = function() {
            addMessage('👋 Hello! I\\'m your AI Timetable Assistant. Ask me about schedules, rooms, faculty, or statistics!');
            loadStats();
            loadVisualization('daily-chart', 'daily_distribution');
            loadVisualization('room-chart', 'room_utilization');
            loadVisualization('time-chart', 'time_distribution');
        };
    </script>
</body>
</html>'''
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(template_content)

def start_dashboard_server():
    """Start the Flask dashboard server."""
    create_dashboard_template()
    print("🌐 Starting AI Dashboard Server...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("💬 Features available:")
    print("   • Natural language queries")
    print("   • Interactive visualizations") 
    print("   • Real-time statistics")
    print("   • Schedule management")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    start_dashboard_server()