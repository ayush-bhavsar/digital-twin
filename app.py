from __future__ import annotations

import os
from collections import defaultdict
from typing import Any

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for


load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "digital-twin-demo-secret-key")
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")


DIMENSIONS = {
    "introversion_extroversion": {
        "low": "Introverted",
        "mid": "Ambivert",
        "high": "Extroverted",
        "label_low": "Introverted",
        "label_high": "Extroverted",
    },
    "risk_level": {
        "low": "Cautious",
        "mid": "Balanced",
        "high": "Bold",
        "label_low": "Cautious",
        "label_high": "Bold",
    },
    "logical_emotional": {
        "low": "Emotion-led",
        "mid": "Balanced",
        "high": "Logic-led",
        "label_low": "Emotion-led",
        "label_high": "Logic-led",
    },
    "planning_spontaneity": {
        "low": "Spontaneous",
        "mid": "Flexible",
        "high": "Planner",
        "label_low": "Spontaneous",
        "label_high": "Planner",
    },
}


def scale_question(question_id: int, section: str, text: str, metric_map: dict[str, dict[str, int]], left: str = "1", right: str = "10") -> dict[str, Any]:
    return {
        "id": question_id,
        "section": section,
        "text": text,
        "type": "scale",
        "min": 1,
        "max": 10,
        "left": left,
        "right": right,
        "metric_map": metric_map,
    }


def radio_question(question_id: int, section: str, text: str, options: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": question_id,
        "section": section,
        "text": text,
        "type": "radio",
        "options": options,
    }


QUESTIONS: list[dict[str, Any]] = [
    radio_question(
        1,
        "Habits & Routine",
        "How strictly do you follow a daily routine?",
        [
            {"label": "Very flexible", "scores": {"planning_spontaneity": -12, "risk_level": 2}},
            {"label": "Somewhat flexible", "scores": {"planning_spontaneity": -6, "risk_level": 1}},
            {"label": "Balanced", "scores": {"planning_spontaneity": 0, "risk_level": 0}},
            {"label": "Mostly structured", "scores": {"planning_spontaneity": 7, "risk_level": -1}},
            {"label": "Strictly structured", "scores": {"planning_spontaneity": 12, "risk_level": -3}},
        ],
    ),
    radio_question(
        2,
        "Habits & Routine",
        "How many hours of sleep do you typically get?",
        [
            {"label": "Less than 4 hours", "scores": {"planning_spontaneity": -8, "logical_emotional": -6}},
            {"label": "4–6 hours", "scores": {"planning_spontaneity": -4, "logical_emotional": -3}},
            {"label": "6–8 hours", "scores": {"planning_spontaneity": 6, "logical_emotional": 5}},
            {"label": "8–10 hours", "scores": {"planning_spontaneity": 4, "logical_emotional": 3}},
            {"label": "More than 10 hours", "scores": {"planning_spontaneity": -2, "logical_emotional": -2}},
        ],
    ),
    radio_question(
        3,
        "Habits & Routine",
        "Do you exercise regularly?",
        [
            {"label": "Yes, I do", "scores": {"planning_spontaneity": 5, "introversion_extroversion": 3}},
            {"label": "No, I don’t", "scores": {"planning_spontaneity": -2, "introversion_extroversion": -1}},
        ],
    ),
    radio_question(
        4,
        "Habits & Routine",
        "How often do you plan your week in advance?",
        [
            {"label": "Never", "scores": {"planning_spontaneity": -14}},
            {"label": "Rarely", "scores": {"planning_spontaneity": -8}},
            {"label": "Sometimes", "scores": {"planning_spontaneity": -1}},
            {"label": "Usually", "scores": {"planning_spontaneity": 8}},
            {"label": "Always", "scores": {"planning_spontaneity": 14}},
        ],
    ),
    radio_question(
        5,
        "Habits & Routine",
        "How productive do you feel in mornings vs evenings?",
        [
            {"label": "Much more productive in mornings", "scores": {"planning_spontaneity": 10, "logical_emotional": 4}},
            {"label": "Slightly more productive in mornings", "scores": {"planning_spontaneity": 5, "logical_emotional": 2}},
            {"label": "Same throughout the day", "scores": {"planning_spontaneity": 0, "logical_emotional": 0}},
            {"label": "Slightly more productive in evenings", "scores": {"planning_spontaneity": -4, "logical_emotional": -2}},
            {"label": "Much more productive in evenings", "scores": {"planning_spontaneity": -8, "logical_emotional": -4}},
        ],
    ),
    scale_question(
        6,
        "Values",
        "How important is financial security in your life decisions? (1–10 scale)",
        {"risk_level": {"direction": -1, "weight": 12}, "planning_spontaneity": {"direction": 1, "weight": 8}},
        "Not important",
        "Extremely important",
    ),
    radio_question(
        7,
        "Values",
        "Would you take a pay cut to do work you find more meaningful?",
        [
            {"label": "Yes, I would", "scores": {"logical_emotional": -4, "risk_level": 5}},
            {"label": "No, I wouldn’t", "scores": {"logical_emotional": 3, "planning_spontaneity": 4}},
        ],
    ),
    scale_question(
        8,
        "Values",
        "How important is family in guiding your major life decisions? (1–10 scale)",
        {"introversion_extroversion": {"direction": 1, "weight": 8}, "planning_spontaneity": {"direction": 1, "weight": 4}},
        "Low influence",
        "Very high influence",
    ),
    radio_question(
        9,
        "Values",
        "Which value matters most to you?",
        [
            {"label": "Freedom & Autonomy", "scores": {"risk_level": 5, "planning_spontaneity": -2}},
            {"label": "Security & Stability", "scores": {"planning_spontaneity": 12, "risk_level": -8}},
            {"label": "Achievement & Success", "scores": {"logical_emotional": 7, "planning_spontaneity": 4}},
            {"label": "Connection & Belonging", "scores": {"introversion_extroversion": 10, "logical_emotional": 2}},
            {"label": "Growth & Learning", "scores": {"risk_level": 4, "logical_emotional": 6, "planning_spontaneity": 2}},
        ],
    ),
    scale_question(
        10,
        "Values",
        "How much does social recognition affect your decisions? (1–10 scale)",
        {"introversion_extroversion": {"direction": 1, "weight": 10}, "planning_spontaneity": {"direction": 1, "weight": 2}},
        "Not at all",
        "A great deal",
    ),
    scale_question(
        11,
        "Risk & Uncertainty",
        "How comfortable are you with financial uncertainty? (1–10 scale)",
        {"risk_level": {"direction": 1, "weight": 14}, "planning_spontaneity": {"direction": -1, "weight": 6}},
        "Very uncomfortable",
        "Very comfortable",
    ),
    radio_question(
        12,
        "Risk & Uncertainty",
        "Would you quit a stable job to pursue your passion without a backup plan?",
        [
            {"label": "Yes, I would", "scores": {"risk_level": 14, "planning_spontaneity": -6, "logical_emotional": -4}},
            {"label": "No, I wouldn’t", "scores": {"risk_level": -12, "planning_spontaneity": 8, "logical_emotional": 6}},
        ],
    ),
    radio_question(
        13,
        "Risk & Uncertainty",
        "How do you typically approach major decisions?",
        [
            {"label": "Gather all information before deciding", "scores": {"logical_emotional": 12, "planning_spontaneity": 8}},
            {"label": "Weigh pros and cons carefully", "scores": {"logical_emotional": 10, "planning_spontaneity": 10}},
            {"label": "Go with gut feeling", "scores": {"logical_emotional": -8, "risk_level": 4}},
            {"label": "Seek advice from others", "scores": {"introversion_extroversion": 8, "planning_spontaneity": 2}},
            {"label": "Decide quickly and adjust later", "scores": {"risk_level": 6, "planning_spontaneity": -10}},
        ],
    ),
    scale_question(
        14,
        "Risk & Uncertainty",
        "How much research do you do before making a big purchase? (1–10 scale)",
        {"planning_spontaneity": {"direction": 1, "weight": 12}, "logical_emotional": {"direction": 1, "weight": 8}},
        "Very little",
        "Extensive research",
    ),
    scale_question(
        15,
        "Risk & Uncertainty",
        "How often do you try new things outside your comfort zone? (1–10 scale)",
        {"risk_level": {"direction": 1, "weight": 12}, "introversion_extroversion": {"direction": 1, "weight": 6}},
        "Rarely",
        "Very often",
    ),
    scale_question(
        16,
        "Social & Relationships",
        "Do you find social interactions energizing or draining? (1–10 scale)",
        {"introversion_extroversion": {"direction": 1, "weight": 14}},
        "Draining",
        "Energizing",
    ),
    radio_question(
        17,
        "Social & Relationships",
        "Do you prefer working alone or in a team?",
        [
            {"label": "Strongly prefer working alone", "scores": {"introversion_extroversion": -14}},
            {"label": "Prefer working alone", "scores": {"introversion_extroversion": -8}},
            {"label": "No preference", "scores": {"introversion_extroversion": 0}},
            {"label": "Prefer working in a team", "scores": {"introversion_extroversion": 8}},
            {"label": "Strongly prefer working in a team", "scores": {"introversion_extroversion": 14}},
        ],
    ),
    radio_question(
        18,
        "Social & Relationships",
        "Would you cancel plans to help a friend in need?",
        [
            {"label": "Yes, I would", "scores": {"introversion_extroversion": 8, "logical_emotional": -2}},
            {"label": "No, I wouldn’t", "scores": {"planning_spontaneity": 4, "logical_emotional": 2}},
        ],
    ),
    scale_question(
        19,
        "Social & Relationships",
        "How important is having a large social circle to you? (1–10 scale)",
        {"introversion_extroversion": {"direction": 1, "weight": 12}},
        "Not important",
        "Very important",
    ),
    scale_question(
        20,
        "Social & Relationships",
        "How comfortable are you speaking in front of a group? (1–10 scale)",
        {"introversion_extroversion": {"direction": 1, "weight": 10}, "risk_level": {"direction": 1, "weight": 4}},
        "Very uncomfortable",
        "Very comfortable",
    ),
    radio_question(
        21,
        "Decision Making",
        "How long does it typically take you to make an important decision?",
        [
            {"label": "Instantly", "scores": {"planning_spontaneity": -14, "risk_level": 6}},
            {"label": "A few minutes", "scores": {"planning_spontaneity": -8, "risk_level": 4}},
            {"label": "A few hours", "scores": {"planning_spontaneity": 0, "logical_emotional": 2}},
            {"label": "A few days", "scores": {"planning_spontaneity": 8, "logical_emotional": 8}},
            {"label": "Weeks or more", "scores": {"planning_spontaneity": 14, "logical_emotional": 10}},
        ],
    ),
    scale_question(
        22,
        "Decision Making",
        "How much do you rely on logic vs emotion? (1–10 scale)",
        {"logical_emotional": {"direction": 1, "weight": 16}, "planning_spontaneity": {"direction": 1, "weight": 4}},
        "Emotion",
        "Logic",
    ),
    radio_question(
        23,
        "Decision Making",
        "Do you often second-guess your decisions?",
        [
            {"label": "Yes, I do", "scores": {"logical_emotional": 4, "planning_spontaneity": 6}},
            {"label": "No, I don’t", "scores": {"logical_emotional": 6, "planning_spontaneity": -2}},
        ],
    ),
    scale_question(
        24,
        "Decision Making",
        "When faced with a dilemma, do you seek others' opinions? (1–10 scale)",
        {"introversion_extroversion": {"direction": 1, "weight": 8}, "planning_spontaneity": {"direction": 1, "weight": 4}},
        "Rarely",
        "Very often",
    ),
    radio_question(
        25,
        "Decision Making",
        "How do you handle making a wrong decision?",
        [
            {"label": "Analyze and learn from it", "scores": {"logical_emotional": 10, "planning_spontaneity": 8}},
            {"label": "Accept and move on quickly", "scores": {"planning_spontaneity": -6, "risk_level": 2}},
            {"label": "Feel regret for a long time", "scores": {"logical_emotional": -10, "planning_spontaneity": 2}},
            {"label": "Try to reverse the decision", "scores": {"planning_spontaneity": 8, "risk_level": -2}},
            {"label": "Seek support from others", "scores": {"introversion_extroversion": 6, "planning_spontaneity": 2}},
        ],
    ),
]


SECTION_ORDER = [
    "Habits & Routine",
    "Values",
    "Risk & Uncertainty",
    "Social & Relationships",
    "Decision Making",
]


def group_questions() -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for question in QUESTIONS:
        grouped[question["section"]].append(question)
    return [{"title": section, "questions": grouped[section]} for section in SECTION_ORDER]


def update_scores(scores: dict[str, float], delta: dict[str, float]) -> None:
    for key, value in delta.items():
        scores[key] = scores.get(key, 50.0) + value


def score_scale(question: dict[str, Any], raw_value: str) -> dict[str, float]:
    value = int(raw_value)
    centered = value - 5.5
    delta: dict[str, float] = {}
    for metric, config in question["metric_map"].items():
        direction = config["direction"]
        weight = config["weight"]
        delta[metric] = delta.get(metric, 0.0) + ((centered / 4.5) * weight * direction)
    return delta


def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, value))


def classify_dimension(score: float, low_label: str, high_label: str) -> str:
    if score >= 60:
        return high_label
    if score <= 40:
        return low_label
    return "Balanced"


def build_archetype(scores: dict[str, float]) -> str:
    extroversion = scores["introversion_extroversion"]
    risk = scores["risk_level"]
    logic = scores["logical_emotional"]
    planning = scores["planning_spontaneity"]

    if extroversion >= 60 and risk >= 60 and planning <= 50:
        return "Visionary Catalyst"
    if extroversion >= 60 and logic >= 60 and planning >= 55:
        return "Strategic Connector"
    if extroversion <= 40 and logic >= 60 and planning >= 60:
        return "Analytical Architect"
    if extroversion <= 40 and planning >= 60 and risk <= 45:
        return "Grounded Strategist"
    if risk >= 60 and planning <= 50:
        return "Adaptive Explorer"
    if planning >= 60 and logic >= 60:
        return "Deliberate Analyst"
    return "Adaptive Navigator"


def build_summary(scores: dict[str, float]) -> str:
    labels = {
        key: classify_dimension(score, values["low"], values["high"])
        for key, score in scores.items()
        for values in [DIMENSIONS[key]]
    }
    archetype = build_archetype(scores)
    return (
        f"Your Digital Twin suggests you are a {archetype.lower()} with a {labels['logical_emotional'].lower()} mindset, "
        f"a {labels['planning_spontaneity'].lower()} decision style, and a {labels['risk_level'].lower()} comfort zone."
    )


def generate_scenarios(scores: dict[str, float]) -> list[dict[str, str]]:
    extroversion = scores["introversion_extroversion"]
    risk = scores["risk_level"]
    logic = scores["logical_emotional"]
    planning = scores["planning_spontaneity"]

    if risk >= 60:
        risky_response = "you move quickly, scan for upside, and commit if the opportunity feels worth the exposure."
    else:
        risky_response = "you slow the moment down, build a fallback, and wait for more certainty before acting."

    if extroversion >= 60:
        conflict_response = "you will likely talk it through directly, using conversation to reset the room."
    else:
        conflict_response = "you will likely observe first, process privately, and step in once the tension is clearer."

    if logic >= 60:
        setback_response = "you will analyze the mistake, extract the lesson, and turn it into a better next move."
    else:
        setback_response = "you may feel the emotional weight first, then recover through support and reflection."

    if planning >= 60:
        uncertainty_response = "you create structure around uncertainty and reduce noise before making a final call."
    else:
        uncertainty_response = "you prefer to test the waters, adapt as you go, and keep options open."

    return [
        {"title": "In a risky situation", "body": f"You are likely to {risky_response}"},
        {"title": "During a team disagreement", "body": f"You are likely to {conflict_response}"},
        {"title": "After a wrong decision", "body": f"You are likely to {setback_response}"},
        {"title": "When facing uncertainty", "body": f"You are likely to {uncertainty_response}"},
    ]


def build_profile(responses: dict[str, str]) -> dict[str, Any]:
    scores = {key: 50.0 for key in DIMENSIONS}

    for question in QUESTIONS:
        response = responses.get(str(question["id"]))
        if not response:
            continue
        if question["type"] == "scale":
            update_scores(scores, score_scale(question, response))
            continue
        selected_option = next((option for option in question["options"] if option["label"] == response), None)
        if selected_option:
            update_scores(scores, selected_option["scores"])

    for key in scores:
        scores[key] = clamp_score(scores[key])

    labels = {
        "introversion_extroversion": classify_dimension(scores["introversion_extroversion"], "Introverted", "Extroverted"),
        "risk_level": classify_dimension(scores["risk_level"], "Cautious", "Bold"),
        "logical_emotional": classify_dimension(scores["logical_emotional"], "Emotion-led", "Logic-led"),
        "planning_spontaneity": classify_dimension(scores["planning_spontaneity"], "Spontaneous", "Planner"),
    }

    return {
        "scores": scores,
        "labels": labels,
        "archetype": build_archetype(scores),
        "summary": build_summary(scores),
        "scenarios": generate_scenarios(scores),
        "recommendation": "Lean into deliberate experimentation: keep your strongest strengths, but create a small feedback loop before major decisions.",
        "answers": responses,
    }


@app.route("/")
def home() -> str:
    return render_template("home.html", active_page="home")


@app.route("/overview")
def overview() -> str:
    return render_template("overview.html", active_page="overview")


@app.route("/methodology")
def methodology() -> str:
    return render_template("methodology.html", active_page="methodology")


@app.route("/assessment", methods=["GET"])
def assessment() -> str:
    return render_template(
        "assessment.html",
        active_page="assessment",
        sections=group_questions(),
        responses=session.get("responses", {}),
    )


@app.route("/submit", methods=["POST"])
def submit_assessment() -> str:
    responses = {key[1:]: value for key, value in request.form.items() if key.startswith("q") and value}
    answered_questions = len(responses)
    if answered_questions < len(QUESTIONS):
        flash("Please answer every question to generate your Digital Twin profile.", "warning")
        session["responses"] = responses
        return redirect(url_for("assessment"))

    profile = build_profile(responses)
    session["responses"] = responses
    session["profile"] = profile
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard() -> str:
    profile = session.get("profile")
    if not profile:
        flash("Complete the assessment first to unlock your dashboard.", "info")
        return redirect(url_for("assessment"))
    return render_template("dashboard.html", active_page="dashboard", profile=profile)


@app.route("/scenarios")
def scenarios() -> str:
    profile = session.get("profile")
    if not profile:
        flash("Complete the assessment first to view predictive scenarios.", "info")
        return redirect(url_for("assessment"))
    return render_template("scenarios.html", active_page="scenarios", profile=profile)


@app.route("/reset")
def reset() -> str:
    session.clear()
    flash("Assessment reset. You can start a fresh Digital Twin profile now.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "1").strip().lower() in {"1", "true", "yes", "on"}
    try:
        port = int(os.getenv("PORT", "5000"))
    except ValueError:
        port = 5000

    app.run(debug=debug, port=port)