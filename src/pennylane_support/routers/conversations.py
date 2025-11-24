from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import SupportConversation, Post, SupportConversationResponse, PostResponse
from typing import List
import re
from ..dependencies import get_current_user, require_admin

router = APIRouter(prefix="/conversations", tags=["conversations"])


# User endpoints
@router.post("/", response_model=SupportConversation)
def create_conversation(data: dict, username: str, session: Session = Depends(get_session)):
    """User creates a support conversation"""
    get_current_user(username, session)

    # Get all existing conversation IDs
    all_conversation_ids = session.exec(select(SupportConversation.id)).all()

    # Extract numbers from conversation IDs (ex: "CONV_001").
    numbers = []
    for conversation_id in all_conversation_ids:
        match = re.search(r"CONV_(\d+)", conversation_id)
        if match:
            numbers.append(int(match.group(1)))

    # Get next number
    next_num = max(numbers) + 1 if numbers else 1
    next_id = f"CONV_{next_num:03d}"

    conversation = SupportConversation(
        # The fact that we have to roll these IDs ourselves is suboptimal...
        # Ideally, these IDs should be managed and auto-incremented in the DB layer.
        id=next_id,
        topic=data["topic"],
        category=data["category"],
        coding_challenge_id=data["coding_challenge_id"],
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@router.get("/{conversation_id}", response_model=SupportConversationResponse)
def get_conversation(conversation_id: str, username: str, session: Session = Depends(get_session)):
    """Get a specific conversation with posts"""
    get_current_user(username, session)

    conversation = session.get(SupportConversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/{conversation_id}/posts/", response_model=List[PostResponse])
def get_posts(conversation_id: str, username: str, session: Session = Depends(get_session)):
    """Get all posts in a conversation"""
    get_current_user(username, session)

    conversation = session.get(SupportConversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation.posts


@router.post("/{conversation_id}/posts/", response_model=Post)
def create_post(
    conversation_id: str, username: str, data: dict, session: Session = Depends(get_session)
):
    """Add a post/reply to a conversation"""
    user = get_current_user(username, session)
    conversation = session.get(SupportConversation, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    post = Post(content=data["content"], user_id=user.id, support_conversation_id=conversation_id)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


# Admin endpoints
@router.get("/", response_model=List[SupportConversationResponse])
def list_conversations(
    username: str,
    session: Session = Depends(get_session),
    challenge_id: str = None,
    category: str = None,
    limit: int = 50,
    offset: int = 0,
):
    """List all conversations (admin only)"""
    require_admin(get_current_user(username, session))

    query = select(SupportConversation)
    if challenge_id:
        query = query.where(SupportConversation.coding_challenge_id == challenge_id)
    if category:
        query = query.where(SupportConversation.category == category)

    return session.exec(query.limit(limit).offset(offset)).all()


@router.patch("/{conversation_id}/", response_model=SupportConversationResponse)
def update_conversation(
    conversation_id: str, data: dict, username: str, session: Session = Depends(get_session)
):
    """Update conversation (admin only)"""
    require_admin(get_current_user(username, session))

    conversation = session.get(SupportConversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    for key, value in data.items():
        if hasattr(conversation, key) and key != "id":
            setattr(conversation, key, value)

    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@router.delete("/{conversation_id}/")
def delete_conversation(
    conversation_id: str, username: str, session: Session = Depends(get_session)
):
    """Delete a conversation (admin only)"""
    require_admin(get_current_user(username, session))

    conversation = session.get(SupportConversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    session.delete(conversation)
    session.commit()
    return {"success": True}
