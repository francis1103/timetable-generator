#!/usr/bin/env python3
"""Comprehensive AI Model Performance Analysis"""

import json
from collections import defaultdict
import math

def analyze_model_performance():
    """Analyze the AI model's performance across multiple metrics."""
    
    print("🤖 AI MODEL PERFORMANCE ANALYSIS")
    print("="*50)
    
    # Load the timetable data
    with open('output/timetable.json', 'r') as f:
        data = json.load(f)
    
    schedule = data['schedule']
    metadata = data['metadata']
    stats = data['statistics']
    fitness = data['fitness_scores']
    
    # 1. CONSTRAINT SATISFACTION METRICS
    print("\n📊 1. CONSTRAINT SATISFACTION METRICS")
    print("-" * 40)
    
    hard_violations = fitness['hard_violations']
    constraint_satisfaction = 100 if hard_violations == 0 else max(0, 100 - hard_violations * 10)
    
    print(f"Hard Constraints: {hard_violations} violations")
    print(f"Constraint Satisfaction Score: {constraint_satisfaction}% {'✅ PERFECT' if constraint_satisfaction == 100 else '⚠️ NEEDS IMPROVEMENT'}")
    
    # 2. OPTIMIZATION EFFICIENCY METRICS
    print("\n🎯 2. OPTIMIZATION EFFICIENCY METRICS")
    print("-" * 40)
    
    total_possible_slots = 35  # 5 days * 7 time slots as mentioned in example
    utilization_rate = (metadata['total_slots'] / total_possible_slots) * 100
    
    print(f"Schedule Utilization: {utilization_rate:.1f}% ({metadata['total_slots']}/{total_possible_slots} slots)")
    print(f"Room Efficiency: {stats['total_room_hours']}/{stats['total_rooms_used']} = {stats['total_room_hours']/stats['total_rooms_used']:.1f} hours/room")
    print(f"Faculty Load Balance: Max={stats['max_faculty_hours']}h, Min={stats['min_faculty_hours']}h, Avg={stats['average_faculty_hours']}h")
    
    load_balance_score = 100 - abs(stats['max_faculty_hours'] - stats['min_faculty_hours']) * 10
    print(f"Load Balance Score: {load_balance_score:.1f}% {'✅ GOOD' if load_balance_score >= 70 else '⚠️ UNBALANCED'}")
    
    # 3. PREFERENCE OPTIMIZATION METRICS
    print("\n💝 3. PREFERENCE OPTIMIZATION METRICS")
    print("-" * 40)
    
    preference_score = fitness['preference_score']
    preference_percentage = min(100, (preference_score / 10) * 100)  # Normalize to 100%
    
    print(f"Preference Score: {preference_score:.2f}/10")
    print(f"Preference Satisfaction: {preference_percentage:.1f}% {'✅ EXCELLENT' if preference_percentage >= 80 else '✅ GOOD' if preference_percentage >= 60 else '⚠️ POOR'}")
    
    # 4. SOFT CONSTRAINT ANALYSIS
    print("\n🔧 4. SOFT CONSTRAINT ANALYSIS")
    print("-" * 40)
    
    soft_penalty = fitness['soft_penalty']
    # Lower soft penalty is better
    soft_score = max(0, 100 - (soft_penalty / 10))
    
    print(f"Soft Penalty: {soft_penalty}")
    print(f"Soft Constraint Score: {soft_score:.1f}% {'✅ EXCELLENT' if soft_score >= 80 else '✅ GOOD' if soft_score >= 60 else '⚠️ NEEDS IMPROVEMENT'}")
    
    # 5. SCHEDULE QUALITY METRICS
    print("\n📅 5. SCHEDULE QUALITY METRICS")
    print("-" * 40)
    
    # Analyze time distribution
    time_slots = defaultdict(int)
    daily_distribution = defaultdict(int)
    faculty_hours = defaultdict(int)
    
    for slot in schedule:
        time_slots[slot['start_time']] += 1
        daily_distribution[slot['day']] += 1
        faculty_hours[slot['faculty']['name']] += 1
    
    # Calculate distribution metrics
    days_used = len(daily_distribution)
    avg_classes_per_day = metadata['total_slots'] / days_used if days_used > 0 else 0
    
    print(f"Days Utilized: {days_used}/5 days")
    print(f"Average Classes/Day: {avg_classes_per_day:.1f}")
    print(f"Time Slot Distribution:")
    for time, count in sorted(time_slots.items()):
        print(f"  {time}: {count} classes")
    
    # 6. OVERALL AI MODEL RATING
    print("\n🏆 6. OVERALL AI MODEL PERFORMANCE")
    print("-" * 40)
    
    # Calculate composite score
    weights = {
        'constraint_satisfaction': 0.35,  # Most important
        'preference_optimization': 0.25,
        'soft_constraints': 0.20,
        'load_balance': 0.15,
        'utilization': 0.05
    }
    
    scores = {
        'constraint_satisfaction': constraint_satisfaction,
        'preference_optimization': preference_percentage,
        'soft_constraints': soft_score,
        'load_balance': load_balance_score,
        'utilization': utilization_rate
    }
    
    overall_score = sum(scores[metric] * weights[metric] for metric in weights)
    
    print(f"Individual Scores:")
    for metric, score in scores.items():
        weight = weights[metric] * 100
        print(f"  {metric.replace('_', ' ').title()}: {score:.1f}% (weight: {weight:.0f}%)")
    
    print(f"\n🎯 OVERALL AI MODEL SCORE: {overall_score:.1f}/100")
    
    # Rating classification
    if overall_score >= 90:
        rating = "🌟 EXCELLENT - Production Ready"
    elif overall_score >= 80:
        rating = "✅ VERY GOOD - Minor optimizations needed"
    elif overall_score >= 70:
        rating = "👍 GOOD - Some improvements recommended"
    elif overall_score >= 60:
        rating = "⚠️ FAIR - Significant improvements needed"
    else:
        rating = "❌ POOR - Major rework required"
    
    print(f"Rating: {rating}")
    
    # 7. RECOMMENDATIONS
    print(f"\n📋 7. AI MODEL RECOMMENDATIONS")
    print("-" * 40)
    
    recommendations = []
    
    if constraint_satisfaction < 100:
        recommendations.append("🔴 CRITICAL: Fix hard constraint violations")
    
    if load_balance_score < 70:
        recommendations.append("🟡 Improve faculty load balancing")
    
    if preference_percentage < 60:
        recommendations.append("🟡 Enhance preference satisfaction algorithms")
    
    if soft_score < 60:
        recommendations.append("🟡 Optimize soft constraint handling")
    
    if utilization_rate < 20:
        recommendations.append("🟡 Increase schedule density for better resource utilization")
    
    if overall_score >= 90:
        recommendations.append("🟢 Model performing excellently! Consider minor fine-tuning")
    elif overall_score >= 80:
        recommendations.append("🟢 Strong performance! Focus on preference optimization")
    
    if not recommendations:
        recommendations.append("🟢 No critical issues found!")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    return overall_score, rating

if __name__ == "__main__":
    analyze_model_performance()