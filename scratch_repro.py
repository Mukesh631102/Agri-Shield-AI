from fastapi import FastAPI, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional

app = FastAPI()

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return {"username": form_data.username}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
