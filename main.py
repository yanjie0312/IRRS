# main.py
from fastapi import FastAPI, Depends, HTTPException          # 导入 FastAPI 主类、依赖注入工具 Depends、HTTP 异常
from sqlalchemy.orm import Session                             # SQLAlchemy 的会话类型（数据库连接的“句柄”）
from pydantic import BaseModel                                 # Pydantic 用来定义请求/响应的数据模型（校验+序列化）
from database import Base, engine, get_db                      # 从自建的 database.py 导入 ORM 基类、数据库引擎、依赖函数 get_db
from models import Todo                                        # 导入你定义的 ORM 模型（对应数据库中的 todos 表）
from fastapi import status                                     # 常量：HTTP 状态码（例如 204、201 等）


# 1️⃣ 创建表（如果第一次运行会自动建）
Base.metadata.create_all(bind=engine)                          # 读取所有继承 Base 的模型元数据，若数据库中没表则在当前 engine 上创建

app = FastAPI(title="IRRS App with DB")                        # 实例化一个 FastAPI 应用，设置标题（/docs 页面会显示）


# Pydantic schemas
class TodoIn(BaseModel):                                       # 定义“输入模型”：客户端提交的数据结构
    text: str                                                  # 只有一个字段 text，类型为字符串

class TodoOut(BaseModel):                                      # 定义“输出模型”：接口返回给客户端的数据结构
    id: int                                                    # 返回包含主键 id
    text: str                                                  # 返回包含文本
    class Config:
        from_attributes = True                                 # Pydantic v2 写法：允许直接把 ORM 对象转成该模型（以前叫 orm_mode=True）


# POST /todos 新增
@app.post("/todos", response_model=TodoOut)                    # 声明一个 POST 路由，路径 /todos，返回体会按 TodoOut 模型格式化
def create_todo(item: TodoIn,                                  # 参数 item：由请求体 JSON 解析并校验成 TodoIn
                db: Session = Depends(get_db)):                # 参数 db：通过 Depends 调用 get_db() 拿到一个数据库会话（请求结束自动关闭）
    new_todo = Todo(text=item.text)                            # 创建 ORM 实例（等价于准备一条 INSERT 语句的值）
    db.add(new_todo)                                           # 把新对象加入事务会话
    db.commit()                                                # 提交事务（真正执行 INSERT 到数据库）
    db.refresh(new_todo)                                       # 刷新对象（让 new_todo 拿到数据库生成的 id 等最新值）
    return new_todo                                            # 返回 ORM 对象；FastAPI 会按 TodoOut 模型序列化为 JSON


# GET /todos 查询
@app.get("/todos", response_model=list[TodoOut])               # 声明一个 GET 路由，返回 TodoOut 的列表
def list_todos(db: Session = Depends(get_db)):                 # 依赖注入拿到 db 会话
    todos = db.query(Todo).all()                               # 查询 todos 表的所有行（SELECT * FROM todos）
    return todos                                               # 返回 ORM 列表；会被序列化为 JSON 数组


# PUT /todos/{todo_id} 更新任务内容
@app.put("/todos/{todo_id}", response_model=TodoOut)           # 声明一个 PUT 路由，带路径参数 todo_id
def update_todo(todo_id: int,                                  # 路径中的 {todo_id} 会被解析为 int 传入
                item: TodoIn,                                  # 请求体的数据，按 TodoIn 校验
                db: Session = Depends(get_db)):                # 注入数据库会话
    todo = db.get(Todo, todo_id)                               # 通过主键查询一条记录（SELECT ... WHERE id=... LIMIT 1）
    if not todo:                                               # 如果不存在，返回 404
        raise HTTPException(status_code=404, detail="Todo not found")

    # 更新字段
    todo.text = item.text                                      # 在 ORM 对象上修改属性（标记为“脏数据”，待提交）
    db.commit()                                                # 提交事务（执行 UPDATE 语句）
    db.refresh(todo)                                           # 刷新对象，确保拿到数据库中的最新值
    return todo                                                # 返回更新后的记录


# DELETE /todos 删除
@app.delete("/todos/{todo_id}",                                # 声明一个 DELETE 路由，带路径参数 todo_id
            status_code=status.HTTP_204_NO_CONTENT)            # 指定成功时返回 204（No Content）
def delete_todo(todo_id: int,                                  # 路径参数：要删除的记录 id
                db: Session = Depends(get_db)):                # 注入数据库会话
    todo = db.get(Todo, todo_id)                               # 先查到要删除的对象
    if not todo:                                               # 不存在则 404
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)                                            # 标记该对象为删除
    db.commit()                                                # 提交事务（执行 DELETE 语句）
    return {"message": "Deleted"}                              # 这里即便返回了消息，客户端仍会看到 204，无响应体（符合 204 语义）
