from typing import Optional

from pydantic import BaseModel, Field, create_model, computed_field
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Workflow(BaseModel):
    id: int
    name: str
    priority: Priority
    created_at: datetime = Field(default_factory=datetime.now)

# create instance
workflow = Workflow(id=1, name="Loan Analysis", priority=Priority.high)

# model_dump() -> Convert Pydantic model to dictionary
print("=== model_dump() ===")
print(workflow.model_dump())

# model_dump() with options
print("\n=== model_dump(exclude) ===")
print(workflow.model_dump(exclude={"created_at"}))

print("\n=== model_dump(mode='json') ===")
print(workflow.model_dump(mode="json"))  # Serialize datetime to string

# model_validate() - Create instance from dict
print("\n=== model_validate() ===")
data = {
    "id": 2,
    "name": "Risk Assessment",
    "priority": "medium"
}
workflow2 = Workflow.model_validate(data)
print(workflow2)

# from JSON string
print("\n=== model_validate_json() ===")
json_str = '{"id": 3, "name": "Compliance Check", "priority": "low"}'
workflow3 = Workflow.model_validate_json(json_str)
print(workflow3)


class ExtractedField(BaseModel):
    name: str
    value: str | int | float
    confidence: float = Field(ge=0, le=1)


class ExtractedEntity(BaseModel):
    entity_type: str
    fields: list[ExtractedField]


class DocumentAnalysis(BaseModel):
    doc_id: int
    filename: str
    entities: list[ExtractedEntity]
    raw_text: Optional[str] = None


# Create nested structure
analysis = DocumentAnalysis(
    doc_id=1,
    filename="loan_disclosure.pdf",
    entities=[
        ExtractedEntity(
            entity_type="borrower",
            fields=[
                ExtractedField(name="name", value="John Doe", confidence=0.98),
                ExtractedField(name="ssn_last4", value="1234", confidence=0.95),
            ]
        ),
        ExtractedEntity(
            entity_type="loan",
            fields=[
                ExtractedField(name="amount", value=450000, confidence=0.99),
                ExtractedField(name="rate", value=6.5, confidence=0.97),
            ]
        )
    ]
)

print("\n=== Nested Model ===")
print(analysis.model_dump(mode="json"))

# Access to nested data
print(f"\n=== Direct Access ===")
print(f"Borrower name: {analysis.entities[0].fields[0].value}")
print(f"Loan amount: {analysis.entities[1].fields[0].value}")


# User defines these fields in the Cape UI
user_defined_schema = {
    "account_number": (str, Field(..., description="Account identifier")),
    "owner_name": (str, Field(..., min_length=1)),
    "balance": (float, Field(ge=0)),
    "is_active": (bool, True),  # Con default
}

# Create model dinamically
DynamicAccount = create_model("DynamicAccount", **user_defined_schema)

# Use it as a normal model
account = DynamicAccount(
    account_number="ACC-12345",
    owner_name="John Doe",
    balance=15000.50
)

print("\n=== Dynamic Model ===")
print(account)
print(account.model_dump())

# Validation works same
print("\n=== Validation still works ===")
try:
    bad_account = DynamicAccount(
        account_number="ACC-999",
        owner_name="",  # Fail min_length
        balance=-100    # Fail ge=0
    )
except Exception as e:
    print(f"Validation error: {e}")


# This comes from the UI/API of Cape - what user defined
schema_from_api = {
    "fields": [
        {"name": "loan_amount", "type": "float", "required": True, "min": 0},
        {"name": "interest_rate", "type": "float", "required": True, "min": 0, "max": 100},
        {"name": "borrower_name", "type": "str", "required": True, "min_length": 1},
        {"name": "loan_date", "type": "str", "required": False, "default": None},
    ]
}

def build_field(field_def: dict) -> tuple:
    """Convert JSON field definition to tuple for create_model()"""
    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
    }
    python_type = type_mapping[field_def["type"]]

    # Build Field constraints
    field_kwargs = {}
    if "min" in field_def:
        field_kwargs["ge"] = field_def["min"]
    if "max" in field_def:
        field_kwargs["le"] = field_def["max"]
    if "min_length" in field_def:
        field_kwargs["min_length"] = field_def["min_length"]

    # Required vs Optional
    if field_def.get("required", True):
        return python_type, Field(..., **field_kwargs)
    else:
        default = field_kwargs.get("default")
        return python_type | None, Field(default, **field_kwargs)

def create_extraction_model(schema: dict, model_name: str = "DynamicExtraction"):
    """Create Pydantic model from JSON schema"""
    fields = {}
    for field_def in schema["fields"]:
        fields[field_def["name"]] = build_field(field_def)
    return create_model(model_name, **fields)

# Create model from JSON schema
LoanExtraction = create_extraction_model(schema_from_api, "LoanExtraction")

# Test with extracted data from document
extracted_data = {
    "loan_amount": 350000.00,
    "interest_rate": 6.75,
    "borrower_name": "Jane Smith",
}

loan = LoanExtraction(**extracted_data)
print("\n=== Dynamic Model from JSON Schema ===")
print(loan.model_dump())

# See the generated schema
print("\n=== Generated Schema ===")
print(LoanExtraction.model_json_schema())


# # # Computed Fields

class LoanAnalysis(BaseModel):
    loan_amount: float = Field(..., gt=0)
    annual_income: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)

    @computed_field
    @property
    def debt_to_income_ratio(self) -> float:
        """Ratio of debt vs income"""
        return round(self.loan_amount / self.annual_income, 2)

    @computed_field
    @property
    def risk_level(self) -> str:
        """Risk level based on credit score"""
        if self.credit_score >= 750 and self.debt_to_income_ratio <= 3:
            return "low"
        elif self.credit_score >= 650 and self.debt_to_income_ratio <= 5:
            return "medium"
        else:
            return "high"

loan = LoanAnalysis(
    loan_amount=350000,
    annual_income=90000,
    credit_score=720
)

print("\n=== Computed Fields ===")
print(loan.model_dump())