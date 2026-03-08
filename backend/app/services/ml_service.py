"""
ML Analytics service using scikit-learn for productivity pattern detection.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)


def analyze_productivity(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze productivity records and return patterns/insights.

    :param records: List of ProductivityAnalytics dicts with date, tasks_completed,
                    tasks_total, category_breakdown, completion_rate
    :return: Structured analytics data
    """
    if not records:
        return {
            "best_hour": None,
            "best_day": None,
            "top_category": None,
            "procrastination_index": 0.0,
            "weekly_trend": [],
            "category_chart": {},
            "completion_chart": [],
        }

    try:
        import pandas as pd
        import numpy as np

        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        df["day_of_week"] = df["date"].dt.day_name()
        df["completion_rate"] = df.get("completion_rate", pd.Series([0.0] * len(df)))

        # Best day of week
        day_rates = df.groupby("day_of_week")["completion_rate"].mean()
        best_day = day_rates.idxmax() if not day_rates.empty else None

        # Top category by completion
        category_data: Dict[str, List[float]] = {}
        for _, row in df.iterrows():
            breakdown = row.get("category_breakdown", {}) or {}
            for cat, val in breakdown.items():
                if cat not in category_data:
                    category_data[cat] = []
                if isinstance(val, dict):
                    rate = val.get("rate", 0.0)
                else:
                    rate = float(val) if val else 0.0
                category_data[cat].append(rate)

        top_category = None
        if category_data:
            avg_rates = {cat: sum(vals) / len(vals) for cat, vals in category_data.items()}
            top_category = max(avg_rates, key=avg_rates.get)

        # Procrastination index (rate of tasks not completed / total)
        total_tasks = df["tasks_total"].sum()
        completed_tasks = df["tasks_completed"].sum()
        procrastination_index = (
            round(1.0 - (completed_tasks / total_tasks), 3) if total_tasks > 0 else 0.0
        )

        # Weekly trend for Plotly
        weekly = (
            df.groupby("date")["completion_rate"]
            .mean()
            .reset_index()
            .tail(30)
        )
        completion_chart = [
            {"date": row["date"].strftime("%Y-%m-%d"), "rate": round(row["completion_rate"], 3)}
            for _, row in weekly.iterrows()
        ]

        # Category breakdown for pie chart
        category_totals: Dict[str, int] = {}
        for _, row in df.iterrows():
            breakdown = row.get("category_breakdown", {}) or {}
            for cat, val in breakdown.items():
                count = val.get("count", 0) if isinstance(val, dict) else int(val or 0)
                category_totals[cat] = category_totals.get(cat, 0) + count

        return {
            "best_day": best_day,
            "top_category": top_category,
            "procrastination_index": procrastination_index,
            "completion_chart": completion_chart,
            "category_chart": category_totals,
            "total_completed": int(completed_tasks),
            "total_tasks": int(total_tasks),
        }

    except Exception as exc:
        logger.error("ML analysis failed: %s", exc)
        return {
            "best_day": None,
            "top_category": None,
            "procrastination_index": 0.0,
            "completion_chart": [],
            "category_chart": {},
            "error": str(exc),
        }


def generate_recommendations(analytics: Dict[str, Any], language_data: List[Dict]) -> Dict[str, Any]:
    """
    Generate scheduling recommendations based on historical productivity patterns.
    """
    suggestions = []

    procrastination = analytics.get("procrastination_index", 0.0)
    if procrastination > 0.5:
        suggestions.append("Your task completion rate is below 50%. Try breaking tasks into smaller steps.")
    elif procrastination > 0.3:
        suggestions.append("Consider time-blocking to improve your task completion rate.")
    else:
        suggestions.append("Great job! You're maintaining a good completion rate. Keep it up!")

    best_day = analytics.get("best_day")
    if best_day:
        suggestions.append(f"You tend to be most productive on {best_day}s. Schedule important tasks then.")

    top_category = analytics.get("top_category")
    if top_category:
        suggestions.append(f"Your strongest category is '{top_category}'. Use this momentum for other areas.")

    if language_data:
        total_words = sum(d.get("words_learned", 0) for d in language_data)
        if total_words < 50:
            suggestions.append("Try to learn at least 10 new vocabulary words daily for effective language learning.")
        else:
            suggestions.append(f"You've learned {total_words} words this period. Excellent progress!")

    suggestions.append("Review flashcards daily for 15-20 minutes to maintain spaced repetition benefits.")

    return {
        "best_day": best_day,
        "top_category": top_category,
        "procrastination_index": procrastination,
        "suggestions": suggestions,
        "chart_data": {
            "completion_trend": analytics.get("completion_chart", []),
            "category_breakdown": analytics.get("category_chart", {}),
        },
    }


def cluster_tasks(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Use KMeans clustering to group tasks by category similarity.
    Returns cluster assignments for visualization.
    """
    if len(tasks) < 3:
        return {"clusters": [], "error": "Need at least 3 tasks for clustering"}

    try:
        import numpy as np
        from sklearn.preprocessing import LabelEncoder
        from sklearn.cluster import KMeans

        categories = [t.get("category", "personal") for t in tasks]
        priorities = [t.get("priority", "medium") for t in tasks]

        le_cat = LabelEncoder()
        le_pri = LabelEncoder()

        cat_encoded = le_cat.fit_transform(categories).reshape(-1, 1)
        pri_encoded = le_pri.fit_transform(priorities).reshape(-1, 1)

        X = np.hstack([cat_encoded, pri_encoded])

        n_clusters = min(4, len(tasks))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        clusters = []
        for i, task in enumerate(tasks):
            clusters.append({
                "task_id": str(task.get("id", "")),
                "title": task.get("title", ""),
                "cluster": int(labels[i]),
            })

        return {"clusters": clusters, "n_clusters": n_clusters}

    except Exception as exc:
        logger.error("Task clustering failed: %s", exc)
        return {"clusters": [], "error": str(exc)}
