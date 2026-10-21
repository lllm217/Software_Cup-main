"""Guest onboarding -> real questionnaire profile -> one-use main-app handoff."""
import json
import secrets
import time
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from agents.accessibility_profile import build_accessibility_profile
from db.database import get_db
from db import crud
from utils.security import create_access_token, decode_access_token
from config import settings

router = APIRouter(prefix="/api/accessibility", tags=["六题画像"])
# Single-worker local deployment. Expiring tickets contain no user data in URL.
_handoffs = {}


def _identity(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
    payload = decode_access_token(token) if token else None
    if not payload or not str(payload.get("student_id", "")).startswith("accessible_"):
        raise HTTPException(401, "画像会话已过期，请重新开始")
    return payload


@router.post("/session")
async def start_session(db: AsyncSession = Depends(get_db)):
    if len(settings.JWT_SECRET) < 32:
        raise HTTPException(503, "请配置至少32位的 JWT_SECRET 后启动服务")
    student_id = "accessible_" + secrets.token_hex(16)
    name = "学习者" + student_id[-4:]
    await crud.create_student(db, id=student_id, student_name=name)
    await db.commit()
    return {"student_id": student_id, "student_name": name,
            "access_token": create_access_token(name, student_id)}


class ProfileRequest(BaseModel):
    answers: dict[str, list[str]]
    course: Literal["人工智能导论", "软件安全", "软件安全技术"]
    scores: list[Annotated[int, Field(strict=True, ge=1, le=5)]] = Field(default_factory=list, max_length=6)


@router.post("/profile")
async def submit_profile(req: ProfileRequest, identity=Depends(_identity), db: AsyncSession = Depends(get_db)):
    if req.scores and (len(req.scores) != 6 or any(type(v) is not int or not 1 <= v <= 5 for v in req.scores)):
        raise HTTPException(422, "评分必须为六个1至5之间的整数")
    try:
        profile, summary, mapped, focus_min = build_accessibility_profile(req.answers, req.course, req.scores)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    student_id = identity["student_id"]
    if not await crud.get_student(db, student_id):
        raise HTTPException(401, "画像会话不存在，请重新开始")
    await crud.update_student(db, student_id, **profile)
    await crud.upsert_course_profile(db, student_id, profile["course"], profile)
    # Keep raw six answers, optional SSVEP scores and mapped answers for audit/recovery.
    stored = {"source": "accessibility-six-v1", "supplemental": req.answers,
              "ssvep_scores": req.scores, "mapped": mapped}
    await crud.upsert_questionnaire(db, student_id, json.dumps(stored, ensure_ascii=False),
                                   json.dumps(profile, ensure_ascii=False), summary, course=profile["course"])
    await crud.upsert_study_setting(db, student_id, daily_goal=3, focus_min=focus_min,
                                   break_min=5, course=profile["course"])
    await db.commit()
    # Ticket is issued only after all DB writes succeed. Expire/reject replay.
    now = time.monotonic()
    for key in list(_handoffs):
        if _handoffs[key][1] < now:
            del _handoffs[key]
    ticket = secrets.token_urlsafe(32)
    _handoffs[ticket] = (student_id, now + 120)
    return {"completed": True, "profile": profile, "summary": summary,
            "student_id": student_id, "handoff": ticket, "algorithm": "questionnaire_rules.derive_profile"}


class HandoffRequest(BaseModel):
    handoff: str = Field(min_length=20, max_length=100)


@router.post("/handoff")
async def exchange_handoff(req: HandoffRequest, db: AsyncSession = Depends(get_db)):
    entry = _handoffs.pop(req.handoff, None)
    if not entry or entry[1] < time.monotonic():
        raise HTTPException(401, "跳转凭据已过期或已使用，请返回问卷重试")
    student = await crud.get_student(db, entry[0])
    if not student:
        raise HTTPException(401, "学习者不存在")
    record = await crud.get_questionnaire(db, student.id, course=student.course)
    if not record:
        raise HTTPException(409, "画像尚未保存")
    return {"student_id": student.id, "student_name": student.student_name,
            "access_token": create_access_token(student.student_name, student.id),
            "profile": json.loads(record.derived), "summary": record.summary,
            "completed": True,
            "register_date": student.create_time.strftime("%Y-%m-%d")}
