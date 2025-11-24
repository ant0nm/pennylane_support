from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import CodingChallenge, CodingChallengeResponse
from typing import List
from ..dependencies import get_current_user

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.get("/", response_model=List[CodingChallengeResponse])
def list_challenges(
    username: str, session: Session = Depends(get_session), limit: int = 50, offset: int = 0
):
    get_current_user(username, session)

    return session.exec(select(CodingChallenge).limit(limit).offset(offset)).all()


@router.get("/{challenge_id}", response_model=CodingChallengeResponse)
def get_challenge(challenge_id: str, username: str, session: Session = Depends(get_session)):
    get_current_user(username, session)

    challenge = session.get(CodingChallenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge
