


'''
memory.create_user_memories(
message="""
I enjoy hiking in the mountains on weekends,
reading science fiction novels before bed,
cooking new recipes from different cultures,
playing chess with friends,
and attending live music concerts whenever possible.
Photography has become a recent passion of mine, especially capturing landscapes and street scenes.
I also like to meditate in the mornings and practice yoga to stay centered.
""",
user_id=john_doe_id,
)

memories = memory.get_user_memories(user_id=john_doe_id)
print("John Doe's memories:")
for i, m in enumerate(memories):
    print(f"{i}: {m.memory} - {m.topics}")

jane_doe_id = "jane_doe@example.com"

# Send a history of messages and add memories
memory_db.clear()

memory.create_user_memories(
messages=[
Message(role="user", content="My name is Jane Doe"),
Message(role="assistant", content="That is great!"),
Message(role="user", content="I like to play chess"),
Message(role="assistant", content="That is great!"),
],
user_id=jane_doe_id,
)

memories = memory.get_user_memories(user_id=jane_doe_id)
print("Jane Doe's memories:")
for i, m in enumerate(memories):
    print(f"{i}: {m.memory} - {m.topics}")
    '''