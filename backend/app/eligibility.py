# backend/app/eligibility.py

from typing import Dict, List
from sqlalchemy.orm import Session
from . import models

def _compare(user_val, operator: str, rule_val: str) -> bool:
    """Simple comparison helper.
    Supports '=', '<=', '>=', 'in'. Numeric strings are compared as floats when possible.
    """
    try:
        user_num = float(user_val)
        rule_num = float(rule_val)
        if operator == "=":
            return user_num == rule_num
        if operator == "<=":
            return user_num <= rule_num
        if operator == ">=":
            return user_num >= rule_num
    except Exception:
        # fall back to string comparison
        if operator == "=":
            return str(user_val) == str(rule_val)
        if operator.lower() == "in":
            return str(user_val) in [v.strip() for v in rule_val.split(",")]
    return False

def evaluate(scheme_id: int, user_data: Dict, db: Session) -> Dict:
    """Evaluate eligibility rules for a scheme against supplied user data.
    Returns a dict compatible with `EligibilityResult`.
    """
    rules: List[models.EligibilityRule] = (
        db.query(models.EligibilityRule)
        .filter(models.EligibilityRule.scheme_id == scheme_id)
        .all()
    )
    matched_fields: List[str] = []
    missing_fields: List[str] = []
    for rule in rules:
        field = rule.field
        if field not in user_data:
            missing_fields.append(field)
            continue
        user_val = user_data[field]
        if _compare(user_val, rule.operator, rule.value):
            matched_fields.append(field)
        else:
            missing_fields.append(field)
    if matched_fields and not missing_fields:
        status = "eligible"
    elif matched_fields:
        status = "needs_more_info"
    else:
        status = "not_eligible"
    return {
        "scheme_id": scheme_id,
        "status": status,
        "missing_fields": missing_fields,
        "matched_fields": matched_fields,
    }
