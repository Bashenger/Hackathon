from agent.router import determine_routing_intent

queries = [
    "What is the leave policy?",
    "Tell me a joke",
    "Show me the employee handbook",
    "What is machine learning?"
]

for query in queries:

    result = determine_routing_intent(query)

    print(f"Query: {query}")
    print(f"Route: {result}")
    print("-" * 30)