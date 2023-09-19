from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated
from pydantic import BaseModel
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# @app.get('/')
# async def index():
#     return "Welcome to Song-Lib"

class PostBase(BaseModel):
    title: str
    description: str
    user_id: int

class UserBase(BaseModel):
    username: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependancy = Annotated[Session, Depends(get_db)]


@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user:UserBase, db:db_dependancy):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    return "Success!"

@app.get("/users/", status_code=status.HTTP_200_OK)
async def get_user(db:db_dependancy):
    users = db.query(models.User).all()
    return users

@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_one_user(user_id:int, db:db_dependancy):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user:UserBase, user_id:int, db:db_dependancy):
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if target_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    target_user.username = user.username
    db.commit()
    return target_user

@app.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id:int, db:db_dependancy):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"Deleted user: ": user_id}