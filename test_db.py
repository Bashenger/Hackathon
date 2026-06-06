from memory.database import *

create_tables()

delete_session("demo_user")

create_session("demo_user")

save_message(
    "demo_user",
    "user",
    "What is the leave policy?"
)

save_message(
    "demo_user",
    "assistant",
    "Employees receive 20 days of leave."
)

save_preference(
    "demo_user",
    "response_style",
    "detailed"
)

print("\n=== CHAT HISTORY ===")
print(get_chat_history("demo_user"))

print("\n=== RECENT MESSAGES ===")
print(get_recent_messages("demo_user"))

print("\n=== USER PREFERENCES ===")
print(get_preferences("demo_user"))

print("\n=== STATS ===")
print("Sessions:", get_session_count())
print("Messages:", get_message_count())