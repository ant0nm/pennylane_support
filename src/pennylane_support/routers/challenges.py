from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import CodingChallenge, CodingChallengeResponse
from typing import List

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.get("/", response_model=List[CodingChallengeResponse])
def list_challenges(
    session: Session = Depends(get_session), limit: int = 50, offset: int = 0
) -> List[CodingChallenge]:
    return session.exec(select(CodingChallenge).limit(limit).offset(offset)).all()


@router.get("/{challenge_id}", response_model=CodingChallengeResponse)
def get_challenge(challenge_id: str, session: Session = Depends(get_session)) -> CodingChallenge:
    challenge = session.get(CodingChallenge, challenge_id)

    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    return challenge
