"""Utility module for BMI Calculator.

Contains BMI calculation logic, input validation, category classification,
health recommendations, ideal weight calculations, and theme definitions.
"""

from datetime import datetime


# ── BMI Categories ──────────────────────────────────────────────────────────

BMI_CATEGORIES = [
    (0, 18.5, "Underweight", "#3498db"),
    (18.5, 25.0, "Normal Weight", "#27ae60"),
    (25.0, 30.0, "Overweight", "#f39c12"),
    (30.0, 35.0, "Obese Class I", "#e67e22"),
    (35.0, 40.0, "Obese Class II", "#e74c3c"),
    (40.0, float("inf"), "Obese Class III", "#c0392b"),
]

RECOMMENDATIONS = {
    "Underweight": (
        "You are underweight. Consider consulting a healthcare provider "
        "about a balanced nutrition plan. Focus on nutrient-dense foods, "
        "healthy fats, and regular strength-building exercises."
    ),
    "Normal Weight": (
        "Congratulations! You are within a healthy weight range. "
        "Maintain your current lifestyle with a balanced diet and "
        "regular physical activity (at least 150 min/week)."
    ),
    "Overweight": (
        "You are slightly overweight. Consider increasing physical "
        "activity and reviewing portion sizes. Aim for 30+ minutes "
        "of moderate exercise most days and reduce processed food intake."
    ),
    "Obese Class I": (
        "You fall in Obese Class I. It is advisable to consult a "
        "healthcare provider for a personalized weight management plan. "
        "Focus on gradual lifestyle changes - diet modification and exercise."
    ),
    "Obese Class II": (
        "You fall in Obese Class II. Please seek medical guidance for "
        "a structured weight-loss program. Monitor blood pressure, "
        "cholesterol, and blood sugar regularly."
    ),
    "Obese Class III": (
        "You fall in Obese Class III (severe obesity). Urgent medical "
        "consultation is recommended. A comprehensive treatment plan "
        "may include dietary therapy, exercise, and possibly bariatric options."
    ),
}

HEALTH_TIPS = [
    "Drink at least 8 glasses of water daily.",
    "Include fruits and vegetables in every meal.",
    "Exercise for at least 30 minutes most days of the week.",
    "Get 7-9 hours of sleep each night.",
    "Limit processed foods and added sugars.",
    "Practice mindful eating - eat slowly and without distractions.",
    "Maintain a food diary to track your intake.",
    "Choose whole grains over refined grains.",
    "Reduce sodium intake to support heart health.",
    "Schedule regular health check-ups.",
    "Manage stress through meditation or deep breathing.",
    "Avoid sugary drinks; opt for water or herbal tea.",
]

# ── Theme Definitions ───────────────────────────────────────────────────────

LIGHT_THEME = {
    "bg": "#f5f7fa",
    "card_bg": "#ffffff",
    "card_border": "#e0e4e8",
    "text": "#2c3e50",
    "text_secondary": "#7f8c8d",
    "input_bg": "#ffffff",
    "input_border": "#bdc3c7",
    "input_focus": "#3498db",
    "button_primary": "#3498db",
    "button_primary_hover": "#2980b9",
    "button_text": "#ffffff",
    "button_danger": "#e74c3c",
    "button_danger_hover": "#c0392b",
    "button_success": "#27ae60",
    "button_success_hover": "#219a52",
    "button_secondary": "#95a5a6",
    "button_secondary_hover": "#7f8c8d",
    "progress_bg": "#ecf0f1",
    "header_bg": "#2c3e50",
    "header_text": "#ffffff",
    "sidebar_bg": "#34495e",
    "sidebar_text": "#ecf0f1",
    "sidebar_active": "#3498db",
    "table_header_bg": "#34495e",
    "table_header_text": "#ffffff",
    "table_row_alt": "#f0f3f5",
    "tooltip_bg": "#2c3e50",
    "tooltip_text": "#ffffff",
    "separator": "#dcdfe3",
    "error": "#e74c3c",
    "success": "#27ae60",
    "warning": "#f39c12",
    "info": "#3498db",
}

DARK_THEME = {
    "bg": "#1a1a2e",
    "card_bg": "#16213e",
    "card_border": "#0f3460",
    "text": "#e0e0e0",
    "text_secondary": "#a0a0a0",
    "input_bg": "#1a1a2e",
    "input_border": "#0f3460",
    "input_focus": "#4fc3f7",
    "button_primary": "#4fc3f7",
    "button_primary_hover": "#29b6f6",
    "button_text": "#1a1a2e",
    "button_danger": "#ef5350",
    "button_danger_hover": "#e53935",
    "button_success": "#66bb6a",
    "button_success_hover": "#4caf50",
    "button_secondary": "#78909c",
    "button_secondary_hover": "#607d8b",
    "progress_bg": "#0f3460",
    "header_bg": "#0f3460",
    "header_text": "#e0e0e0",
    "sidebar_bg": "#0f3460",
    "sidebar_text": "#e0e0e0",
    "sidebar_active": "#4fc3f7",
    "table_header_bg": "#0f3460",
    "table_header_text": "#e0e0e0",
    "table_row_alt": "#1a1a2e",
    "tooltip_bg": "#0f3460",
    "tooltip_text": "#e0e0e0",
    "separator": "#0f3460",
    "error": "#ef5350",
    "success": "#66bb6a",
    "warning": "#ffa726",
    "info": "#4fc3f7",
}


# ── BMI Calculation ─────────────────────────────────────────────────────────

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight (kg) and height (cm)."""
    height_m = height_cm / 100.0
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    return round(weight_kg / (height_m ** 2), 2)


def get_category(bmi: float) -> tuple:
    """Return (category_name, color, recommendation) for a given BMI."""
    for low, high, name, color in BMI_CATEGORIES:
        if low <= bmi < high:
            return name, color, RECOMMENDATIONS.get(name, "")
    name, color = "Obese Class III", "#c0392b"
    return name, color, RECOMMENDATIONS.get(name, "")


def ideal_weight_range(height_cm: float) -> tuple:
    """Return (min_kg, max_kg) for a normal BMI (18.5-24.9) at given height."""
    height_m = height_cm / 100.0
    min_w = round(18.5 * height_m ** 2, 1)
    max_w = round(24.9 * height_m ** 2, 1)
    return min_w, max_w


# ── Input Validation ────────────────────────────────────────────────────────

def validate_name(name: str) -> tuple:
    if not name or not name.strip():
        return False, "Name is required."
    if any(c.isdigit() for c in name):
        return False, "Name should not contain numbers."
    return True, ""


def validate_age(age_str: str) -> tuple:
    if not age_str:
        return False, "Age is required."
    try:
        age = int(age_str)
    except ValueError:
        return False, "Age must be a whole number."
    if age <= 0:
        return False, "Age must be a positive number."
    if age > 150:
        return False, "Please enter a realistic age."
    return True, ""


def validate_gender(gender: str) -> tuple:
    if not gender:
        return False, "Please select a gender."
    return True, ""


def validate_weight(weight_str: str) -> tuple:
    if not weight_str:
        return False, "Weight is required."
    try:
        weight = float(weight_str)
    except ValueError:
        return False, "Weight must be a number."
    if weight <= 0:
        return False, "Weight must be greater than zero."
    if weight > 500:
        return False, "Please enter a realistic weight."
    return True, ""


def validate_height(height_str: str) -> tuple:
    if not height_str:
        return False, "Height is required."
    try:
        height = float(height_str)
    except ValueError:
        return False, "Height must be a number."
    if height <= 0:
        return False, "Height must be greater than zero."
    if height > 300:
        return False, "Please enter a realistic height."
    return True, ""


def validate_all(name: str, age: str, gender: str, weight: str, height: str) -> tuple:
    """Validate all inputs. Returns (is_valid, error_message)."""
    for validator, value in [
        (validate_name, name),
        (validate_age, age),
        (validate_gender, gender),
        (validate_weight, weight),
        (validate_height, height),
    ]:
        ok, msg = validator(value)
        if not ok:
            return False, msg
    return True, ""


# ── Helpers ──────────────────────────────────────────────────────────────────

def format_datetime(dt=None) -> str:
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(dt=None) -> str:
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d")


def bmi_to_progress(bmi: float) -> float:
    """Convert BMI value to a 0-1 progress-bar fraction (0=10, 1=50)."""
    return max(0.0, min(1.0, (bmi - 10) / 40))
