"""
Feedback & Continuous Learning System
Collects satisfaction feedback and retrains preference models over time
"""

import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import pickle
import os

class FeedbackCollector:
    """
    Collects and manages feedback from faculty and students.
    """
    
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Setup SQLite database for feedback storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                user_type TEXT NOT NULL, -- 'faculty' or 'student'
                overall_satisfaction REAL NOT NULL, -- 1-10 scale
                timestamp DATETIME NOT NULL,
                comments TEXT,
                specific_ratings TEXT -- JSON string of specific ratings
            )
        ''')
        
        # Schedule performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id TEXT NOT NULL,
                generation_date DATETIME NOT NULL,
                algorithm_version TEXT,
                performance_metrics TEXT, -- JSON string
                user_adoption_rate REAL,
                avg_satisfaction REAL
            )
        ''')
        
        # Learning events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL, -- 'model_update', 'preference_change', etc.
                timestamp DATETIME NOT NULL,
                details TEXT, -- JSON string
                impact_score REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_feedback(self, feedback_data: Dict) -> str:
        """
        Collect feedback from users.
        
        feedback_data = {
            'schedule_id': 'schedule_001',
            'user_id': 'F001',
            'user_type': 'faculty',
            'overall_satisfaction': 8.5,
            'specific_ratings': {
                'time_preference': 9,
                'room_preference': 7,
                'workload_balance': 8,
                'schedule_clarity': 9
            },
            'comments': 'Great schedule but room 101 is too far from my office'
        }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (
                schedule_id, user_id, user_type, overall_satisfaction,
                timestamp, comments, specific_ratings
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_data['schedule_id'],
            feedback_data['user_id'],
            feedback_data['user_type'],
            feedback_data['overall_satisfaction'],
            datetime.now(),
            feedback_data.get('comments', ''),
            json.dumps(feedback_data.get('specific_ratings', {}))
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return f"feedback_{feedback_id}"
    
    def get_feedback_summary(self, schedule_id: str = None, 
                           user_type: str = None,
                           days_back: int = 30) -> Dict:
        """Get summary of feedback data."""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT user_type, overall_satisfaction, specific_ratings, comments
            FROM feedback 
            WHERE timestamp >= ?
        '''
        params = [datetime.now() - timedelta(days=days_back)]
        
        if schedule_id:
            query += ' AND schedule_id = ?'
            params.append(schedule_id)
        
        if user_type:
            query += ' AND user_type = ?'
            params.append(user_type)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            return {'message': 'No feedback data available'}
        
        # Calculate summaries
        summary = {
            'total_responses': len(df),
            'avg_satisfaction': df['overall_satisfaction'].mean(),
            'satisfaction_by_type': df.groupby('user_type')['overall_satisfaction'].mean().to_dict(),
            'response_distribution': df['user_type'].value_counts().to_dict()
        }
        
        # Analyze specific ratings
        specific_ratings = defaultdict(list)
        for _, row in df.iterrows():
            if row['specific_ratings']:
                ratings = json.loads(row['specific_ratings'])
                for category, rating in ratings.items():
                    specific_ratings[category].append(rating)
        
        summary['specific_ratings_avg'] = {
            category: np.mean(ratings) 
            for category, ratings in specific_ratings.items()
        }
        
        # Extract common themes from comments
        comments = df['comments'].dropna().tolist()
        summary['comment_themes'] = self._analyze_comment_themes(comments)
        
        return summary
    
    def _analyze_comment_themes(self, comments: List[str]) -> Dict:
        """Analyze common themes in feedback comments."""
        # Simple keyword-based theme analysis
        themes = {
            'room_issues': 0,
            'time_issues': 0,
            'workload_issues': 0,
            'positive_feedback': 0,
            'technical_issues': 0
        }
        
        keywords = {
            'room_issues': ['room', 'building', 'location', 'far', 'close'],
            'time_issues': ['time', 'early', 'late', 'schedule', 'hours'],
            'workload_issues': ['workload', 'busy', 'overwhelming', 'too much'],
            'positive_feedback': ['good', 'great', 'excellent', 'perfect', 'satisfied'],
            'technical_issues': ['system', 'error', 'bug', 'problem', 'issue']
        }
        
        for comment in comments:
            comment_lower = comment.lower()
            for theme, theme_keywords in keywords.items():
                if any(keyword in comment_lower for keyword in theme_keywords):
                    themes[theme] += 1
        
        return themes

class ContinuousLearner:
    """
    Implements continuous learning from feedback data.
    """
    
    def __init__(self, feedback_collector: FeedbackCollector):
        self.feedback_collector = feedback_collector
        self.learning_history = []
        self.model_versions = {}
        self.current_weights = self._load_current_weights()
        
    def _load_current_weights(self) -> Dict:
        """Load current preference weights."""
        default_weights = {
            'time_preference': 1.0,
            'room_preference': 1.0,
            'workload_balance': 1.0,
            'schedule_clarity': 1.0,
            'consistency': 1.0
        }
        
        try:
            with open('model_weights.pkl', 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return default_weights
    
    def _save_current_weights(self):
        """Save current preference weights."""
        with open('model_weights.pkl', 'wb') as f:
            pickle.dump(self.current_weights, f)
    
    def analyze_feedback_trends(self, days_back: int = 30) -> Dict:
        """Analyze feedback trends over time."""
        summary = self.feedback_collector.get_feedback_summary(days_back=days_back)
        
        if 'message' in summary:
            return summary
        
        # Identify areas needing improvement
        improvement_areas = []
        specific_ratings = summary.get('specific_ratings_avg', {})
        
        for category, avg_rating in specific_ratings.items():
            if avg_rating < 7.0:  # Threshold for improvement
                improvement_areas.append({
                    'category': category,
                    'current_rating': avg_rating,
                    'improvement_needed': 8.0 - avg_rating
                })
        
        # Check satisfaction trends
        overall_satisfaction = summary.get('avg_satisfaction', 0)
        satisfaction_status = 'excellent' if overall_satisfaction >= 8.5 else \
                           'good' if overall_satisfaction >= 7.0 else \
                           'needs_improvement'
        
        return {
            'summary': summary,
            'improvement_areas': improvement_areas,
            'satisfaction_status': satisfaction_status,
            'learning_recommendations': self._generate_learning_recommendations(improvement_areas)
        }
    
    def _generate_learning_recommendations(self, improvement_areas: List[Dict]) -> List[str]:
        """Generate specific learning recommendations."""
        recommendations = []
        
        for area in improvement_areas:
            category = area['category']
            improvement = area['improvement_needed']
            
            if category == 'time_preference':
                recommendations.append(f"Increase weight for faculty time preferences by {improvement:.1f}x")
            elif category == 'room_preference':
                recommendations.append(f"Improve room assignment algorithm - current satisfaction: {area['current_rating']:.1f}/10")
            elif category == 'workload_balance':
                recommendations.append(f"Enhance workload balancing constraints - gap: {improvement:.1f} points")
            elif category == 'schedule_clarity':
                recommendations.append(f"Improve schedule presentation and communication")
        
        if not recommendations:
            recommendations.append("Current model performance is satisfactory - continue monitoring")
        
        return recommendations
    
    def update_model_weights(self, feedback_analysis: Dict) -> Dict:
        """Update model weights based on feedback analysis."""
        improvement_areas = feedback_analysis.get('improvement_areas', [])
        
        if not improvement_areas:
            return {
                'weights_updated': False,
                'message': 'No weight updates needed - performance satisfactory'
            }
        
        # Calculate weight adjustments
        weight_updates = {}
        learning_rate = 0.1
        
        for area in improvement_areas:
            category = area['category']
            improvement_needed = area['improvement_needed']
            
            # Calculate adjustment factor
            adjustment = learning_rate * (improvement_needed / 10.0)
            
            if category in self.current_weights:
                old_weight = self.current_weights[category]
                new_weight = min(3.0, old_weight + adjustment)  # Cap at 3.0
                
                weight_updates[category] = {
                    'old_weight': old_weight,
                    'new_weight': new_weight,
                    'adjustment': new_weight - old_weight
                }
                
                self.current_weights[category] = new_weight
        
        # Save updated weights
        self._save_current_weights()
        
        # Record learning event
        self._record_learning_event('weight_update', {
            'updates': weight_updates,
            'trigger': 'feedback_analysis'
        })
        
        return {
            'weights_updated': True,
            'updates': weight_updates,
            'new_weights': self.current_weights.copy()
        }
    
    def _record_learning_event(self, event_type: str, details: Dict):
        """Record a learning event."""
        conn = sqlite3.connect(self.feedback_collector.db_path)
        cursor = conn.cursor()
        
        # Calculate impact score based on number of changes
        impact_score = len(details.get('updates', {})) * 0.1
        
        cursor.execute('''
            INSERT INTO learning_events (event_type, timestamp, details, impact_score)
            VALUES (?, ?, ?, ?)
        ''', (
            event_type,
            datetime.now(),
            json.dumps(details),
            impact_score
        ))
        
        conn.commit()
        conn.close()
        
        self.learning_history.append({
            'event_type': event_type,
            'timestamp': datetime.now(),
            'details': details,
            'impact_score': impact_score
        })
    
    def generate_weekly_learning_report(self) -> Dict:
        """Generate a weekly learning report."""
        # Get recent feedback
        feedback_analysis = self.analyze_feedback_trends(days_back=7)
        
        # Get learning events from past week
        conn = sqlite3.connect(self.feedback_collector.db_path)
        query = '''
            SELECT event_type, details, impact_score, timestamp
            FROM learning_events 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        '''
        
        recent_events = pd.read_sql_query(
            query, conn, 
            params=[datetime.now() - timedelta(days=7)]
        )
        conn.close()
        
        # Generate report
        report = {
            'report_period': f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
            'feedback_summary': feedback_analysis.get('summary', {}),
            'satisfaction_trend': feedback_analysis.get('satisfaction_status', 'unknown'),
            'learning_events': len(recent_events),
            'total_impact_score': recent_events['impact_score'].sum() if not recent_events.empty else 0,
            'recommendations': feedback_analysis.get('learning_recommendations', []),
            'next_actions': self._determine_next_actions(feedback_analysis)
        }
        
        return report
    
    def _determine_next_actions(self, feedback_analysis: Dict) -> List[str]:
        """Determine next actions based on analysis."""
        actions = []
        
        satisfaction_status = feedback_analysis.get('satisfaction_status', '')
        improvement_areas = feedback_analysis.get('improvement_areas', [])
        
        if satisfaction_status == 'needs_improvement':
            actions.append("🔴 URGENT: Schedule major model improvements")
            actions.append("📞 Contact faculty/students for detailed feedback")
        
        if len(improvement_areas) > 2:
            actions.append("🔧 Implement targeted algorithm improvements")
        
        if satisfaction_status == 'excellent':
            actions.append("✅ Continue current approach - monitor for consistency")
            actions.append("📊 Consider expanding to additional departments")
        
        actions.append("📅 Schedule next feedback collection cycle")
        
        return actions

def simulate_feedback_collection():
    """Simulate a feedback collection and learning cycle."""
    print("🔹 FEEDBACK & CONTINUOUS LEARNING DEMO")
    print("="*50)
    
    # Initialize systems
    collector = FeedbackCollector("demo_feedback.db")
    learner = ContinuousLearner(collector)
    
    # Simulate collecting feedback
    print("📝 Simulating Feedback Collection...")
    
    sample_feedback = [
        {
            'schedule_id': 'schedule_001',
            'user_id': 'F001',
            'user_type': 'faculty',
            'overall_satisfaction': 8.5,
            'specific_ratings': {
                'time_preference': 9,
                'room_preference': 6,  # Low rating
                'workload_balance': 8,
                'schedule_clarity': 9
            },
            'comments': 'Good schedule but room assignments could be better'
        },
        {
            'schedule_id': 'schedule_001',
            'user_id': 'F002',
            'user_type': 'faculty',
            'overall_satisfaction': 7.0,
            'specific_ratings': {
                'time_preference': 6,  # Low rating
                'room_preference': 8,
                'workload_balance': 7,
                'schedule_clarity': 8
            },
            'comments': 'Early morning classes are challenging'
        },
        {
            'schedule_id': 'schedule_001',
            'user_id': 'S001',
            'user_type': 'student',
            'overall_satisfaction': 8.0,
            'specific_ratings': {
                'time_preference': 8,
                'room_preference': 8,
                'workload_balance': 7,
                'schedule_clarity': 9
            },
            'comments': 'Schedule is clear and well-organized'
        }
    ]
    
    # Collect feedback
    feedback_ids = []
    for feedback in sample_feedback:
        feedback_id = collector.collect_feedback(feedback)
        feedback_ids.append(feedback_id)
    
    print(f"   ✅ Collected {len(feedback_ids)} feedback responses")
    
    # Analyze feedback trends
    print(f"\n📊 Analyzing Feedback Trends...")
    analysis = learner.analyze_feedback_trends()
    
    print(f"   Average Satisfaction: {analysis['summary']['avg_satisfaction']:.1f}/10")
    print(f"   Status: {analysis['satisfaction_status'].title()}")
    print(f"   Areas needing improvement: {len(analysis['improvement_areas'])}")
    
    for area in analysis['improvement_areas']:
        print(f"     • {area['category']}: {area['current_rating']:.1f}/10 (needs +{area['improvement_needed']:.1f})")
    
    # Update model weights
    print(f"\n🧠 Updating Model Weights...")
    weight_update = learner.update_model_weights(analysis)
    
    if weight_update['weights_updated']:
        print(f"   ✅ Weights updated for {len(weight_update['updates'])} categories:")
        for category, update in weight_update['updates'].items():
            print(f"     • {category}: {update['old_weight']:.2f} → {update['new_weight']:.2f} (+{update['adjustment']:.2f})")
    else:
        print(f"   ℹ️ No weight updates needed")
    
    # Generate learning recommendations
    print(f"\n💡 Learning Recommendations:")
    for rec in analysis['learning_recommendations']:
        print(f"   • {rec}")
    
    # Generate weekly report
    print(f"\n📋 Weekly Learning Report:")
    report = learner.generate_weekly_learning_report()
    
    print(f"   Period: {report['report_period']}")
    print(f"   Learning Events: {report['learning_events']}")
    print(f"   Total Impact Score: {report['total_impact_score']:.2f}")
    print(f"   Next Actions:")
    for action in report['next_actions']:
        print(f"     {action}")
    
    # Cleanup demo database
    if os.path.exists("demo_feedback.db"):
        os.remove("demo_feedback.db")
    
    print(f"\n✅ Feedback & Continuous Learning System Demonstrated!")
    print(f"   • Automated feedback collection ✅")
    print(f"   • Trend analysis and insights ✅")
    print(f"   • Dynamic weight adjustment ✅")
    print(f"   • Continuous improvement cycle ✅")

if __name__ == "__main__":
    simulate_feedback_collection()