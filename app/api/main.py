from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.db.models import User, Conversation, Message, ApprovalQueue, PersonaSettings, ApprovalStatus
from sqlalchemy import select, update
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
import json

app = FastAPI(title=settings.PROJECT_NAME)
templates = Jinja2Templates(directory="app/templates")

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    # Simple validation for now
    if token == "authenticated": # placeholder for actual JWT logic
        return settings.ADMIN_USERNAME
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value="authenticated")
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/")
async def dashboard_home(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        await get_current_user(request)
    except HTTPException:
        return RedirectResponse(url="/login")

    users_result = await db.execute(select(User))
    users = users_result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "users": users})

@app.get("/approvals")
async def view_approvals(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        await get_current_user(request)
    except HTTPException:
        return RedirectResponse(url="/login")

    stmt = select(ApprovalQueue).where(ApprovalQueue.status == ApprovalStatus.PENDING)
    result = await db.execute(stmt)
    pending_approvals = result.scalars().all()
    return templates.TemplateResponse("approvals.html", {"request": request, "approvals": pending_approvals})

@app.get("/settings")
async def view_settings(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        await get_current_user(request)
    except HTTPException:
        return RedirectResponse(url="/login")

    stmt = select(PersonaSettings)
    result = await db.execute(stmt)
    personas = result.scalars().all()
    return templates.TemplateResponse("settings.html", {"request": request, "personas": personas})

@app.post("/api/approve/{item_id}")
async def approve_item(item_id: int, db: AsyncSession = Depends(get_db)):
    # In a real scenario, this would trigger the bot to send the message
    stmt = update(ApprovalQueue).where(ApprovalQueue.id == item_id).values(status=ApprovalStatus.APPROVED)
    await db.execute(stmt)
    await db.commit()
    return {"status": "success"}

@app.post("/api/reject/{item_id}")
async def reject_item(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = update(ApprovalQueue).where(ApprovalQueue.id == item_id).values(status=ApprovalStatus.REJECTED)
    await db.execute(stmt)
    await db.commit()
    return {"status": "success"}

@app.post("/api/settings/{persona_id}")
async def update_settings(
    persona_id: int,
    tone: str = Form(...),
    style: str = Form(...),
    system_prompt: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    stmt = update(PersonaSettings).where(PersonaSettings.id == persona_id).values(
        tone=tone,
        style=style,
        system_prompt=system_prompt
    )
    await db.execute(stmt)
    await db.commit()
    return RedirectResponse(url="/settings", status_code=status.HTTP_302_FOUND)
