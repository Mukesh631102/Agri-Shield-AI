from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from . import service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse)
async def advisory_register_page(request: Request):
    """Show personalized alerts registration page"""
    return templates.TemplateResponse(request=request, name="personalized_alerts.html", context={"request": request})

@router.post("/register")
async def advisory_register_post(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    city: str = Form(...),
    crop: str = Form(...),
    db: Session = Depends(get_db)
):
    """Register farmer and send initial weather alert"""
    # Save to database
    new_farmer = models.AdvisoryFarmer(name=name, phone=phone, city=city, crop=crop)
    db.add(new_farmer)
    db.commit()
    
    # Get current weather
    temp, condition = service.get_weather(city)
    
    if temp is not None:
        msg = f"""
🌾 Welcome to Agri Shield Alerts

Farmer: {name}
Crop: {crop}
City: {city}

Current Temperature: {temp}°C
Condition: {condition}

You will receive daily weather updates for your {crop}.
"""
        service.send_alert_sms(phone, msg)
        success_msg = f"Registered successfully! Initial alert sent for {city}."
    else:
        success_msg = "Registered successfully! (Weather data unavailable at the moment)"

    return templates.TemplateResponse(request=request, name="personalized_alerts.html", context={
        "request": request,
        "success": success_msg
    })
