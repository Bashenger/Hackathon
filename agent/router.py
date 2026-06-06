def determine_routing_intent(query: str) -> str:

    keywords = [
        "policy",
        "leave",
        "handbook",
        "onboarding",
        "document",
        "company",
        "vacation",
        "benefits",
        "hr",
        "employee",
        "employees",
        "benefits",
        "pto",
        "holiday",
        "hr",
        "reimbursement",
        "payroll",
        "pay",
        "salary",
        "compensation",
        "expense"

    ]

    if any(
        keyword in query.lower()
        for keyword in keywords
    ):
        return "rag_mode"

    return "general_mode"
