import json
from datetime import datetime
from sqlmodel import Session, select
from src.pennylane_support.database import SessionLocal
from src.pennylane_support.models import User, CodingChallenge, SupportConversation, Post
from pathlib import Path

PENNYLANE_SUPPORT_ADMINS = ["pennylane_support"]


def seed():
    session = SessionLocal()

    # Step 1: Create/seed users from conversation posts
    print("Creating users...")
    users_map = {}  # username -> user.id

    with open(Path(__file__).parent / "data" / "pennylane_support_conversations.json") as f:
        conv_data = json.load(f)

    users_set = set()
    for conversation in conv_data["support_conversations"]:
        for post in conversation["posts"]:
            users_set.add(post["user"])

    for username in users_set:
        existing = session.exec(select(User).where(User.name == username)).first()
        if existing:
            users_map[username] = existing.id
            print(f"  User {username} already exists")
        else:
            is_admin = username in PENNYLANE_SUPPORT_ADMINS
            user = User(name=username, is_admin=is_admin)
            session.add(user)
            session.flush()
            users_map[username] = user.id
            print(f"  Created user {username}")

    session.commit()

    # Step 2: Seed coding challenges
    print("\nCreating coding challenges...")
    with open(Path(__file__).parent / "data" / "pennylane_coding_challenges.json") as f:
        challenges_data = json.load(f)

    for challenge_data in challenges_data["coding_challenges"]:
        existing = session.exec(
            select(CodingChallenge).where(CodingChallenge.id == challenge_data["challenge_id"])
        ).first()

        if existing:
            print(f"  Challenge {challenge_data['challenge_id']} already exists")
            continue

        challenge = CodingChallenge(
            id=challenge_data["challenge_id"],
            title=challenge_data["title"],
            description=challenge_data["description"],
            category=challenge_data["category"],
            difficulty=challenge_data["difficulty"],
            points=challenge_data["points"],
            tags=challenge_data["tags"],
            learning_objectives=challenge_data["learning_objectives"],
            hints=challenge_data["hints"],
        )
        session.add(challenge)
        print(f"  Created challenge {challenge_data['challenge_id']}")

    session.commit()

    # Step 3: Seed support conversations and posts
    print("\nCreating support conversations and posts...")
    with open(Path(__file__).parent / "data" / "pennylane_support_conversations.json") as f:
        conv_data = json.load(f)

    for conversation_data in conv_data["support_conversations"]:
        existing = session.exec(
            select(SupportConversation).where(
                SupportConversation.id == conversation_data["identifier"]
            )
        ).first()

        if existing:
            print(f"  Conversation {conversation_data['identifier']} already exists")
            continue

        conversation = SupportConversation(
            id=conversation_data["identifier"],
            topic=conversation_data["topic"],
            category=conversation_data["category"],
            coding_challenge_id=conversation_data["challenge_id"],
        )
        session.add(conversation)
        session.flush()
        print(f"  Created conversation {conversation_data['identifier']}")

        # Add posts to conversation
        for post_data in conversation_data["posts"]:
            post = Post(
                timestamp=datetime.fromisoformat(post_data["timestamp"].replace("Z", "+00:00")),
                content=post_data["content"],
                user_id=users_map[post_data["user"]],
                support_conversation_id=conversation.id,
            )
            session.add(post)

        session.flush()

    session.commit()
    session.close()
    print("Database seeded successfully!")


if __name__ == "__main__":
    seed()
