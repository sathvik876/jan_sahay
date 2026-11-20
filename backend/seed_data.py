# backend/seed_data.py
"""Simple script to insert a few example schemes and eligibility rules.
Run after creating the database tables:
    .\venv\Scripts\python.exe seed_data.py
"""

from app.db import SessionLocal, Base, engine
from app import models

# Ensure tables exist (in case you haven't run the create_all yet)
Base.metadata.create_all(bind=engine)

example_schemes = [
    {
        "name": "Telangana Student Scholarship",
        "category": "Education",
        "department": "Dept. of Higher Education",
        "state": "Telangana",
        "status": "Verified",
        "rules": [
            {"field": "state", "operator": "=", "value": "Telangana"},
            {"field": "age", "operator": "<=", "value": "25"},
            {"field": "income", "operator": "<=", "value": "200000"},
            {"field": "enrollment", "operator": "=", "value": "college"},
        ],
    },
    {
        "name": "National Agricultural Loan Waiver",
        "category": "Agriculture",
        "department": "Ministry of Agriculture",
        "state": "All",
        "status": "Verified",
        "rules": [
            {"field": "occupation", "operator": "=", "value": "farmer"},
            {"field": "land_holdings", "operator": "<=", "value": "5"},
        ],
    },
    {
        "name": "Senior Citizen Pension Scheme",
        "category": "Social Welfare",
        "department": "Dept. of Social Justice",
        "state": "All",
        "status": "Verified",
        "rules": [
            {"field": "age", "operator": ">=", "value": "60"},
        ],
    },
]

with SessionLocal() as db:
    for s in example_schemes:
        existing = db.query(models.Scheme).filter(models.Scheme.name == s["name"]).first()
        if existing:
            continue
        scheme = models.Scheme(
            name=s["name"],
            category=s["category"],
            department=s["department"],
            state=s["state"],
            status=s["status"],
        )
        db.add(scheme)
        db.flush()  # get generated id
        for r in s["rules"]:
            rule = models.EligibilityRule(
                scheme_id=scheme.id,
                field=r["field"],
                operator=r["operator"],
                value=r["value"],
                source_reference="seed data",
            )
            db.add(rule)
    db.commit()

print("Sample schemes and eligibility rules inserted.")
