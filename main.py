# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import Base, engine, get_db
from models import Todo

app = FastAPI(title="IRRS App with DB")

@app.get("/")
def root():
    return {"ok": True}

@app.get("/healthz")
def health():
    return {"status": "healthy"}
    

# ✅ 修改：不要在模块导入时连库建表，改到启动事件里做
@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        # 也可以在这里做轻量的连接测试，但不要阻塞太久
    except Exception as e:
        # 关键点：即使建表失败，也不要让应用崩；先能 listen 再说
        print(f"[startup] DB init error: {e}")

# ====== 你原有的 Pydantic schemas 与路由保持不变 ======

class TodoIn(BaseModel):
    text: str

class TodoOut(BaseModel):
    id: int
    text: str
    class Config:
        from_attributes = True

@app.post("/todos", response_model=TodoOut)
def create_todo(item: TodoIn, db: Session = Depends(get_db)):
    new_todo = Todo(text=item.text)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.get("/todos", response_model=list[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return todos

@app.put("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, item: TodoIn, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.text = item.text
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Deleted"}
