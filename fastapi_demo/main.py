# powershell 確認版本
# powershell makesure the version
# python --version
# 建立專案
# create project
# mkdir fastapi_demo
# cd fastapi_demo
# 建立 venv 虛擬環境
# python -m venv .venv
# 啟動 vemv 虛擬環境
# .\.venv\Scripts\Activate.ps1
# python -m pip install "fastapi[standard]"

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello FastAPI!"}

@app.get("/hello/{name}")
def hello(name: str):
    return{
        "message": f"Hello, {name}!"
    }

@app.get("/score")
def get_score(name: str):
    scores = {
        "roy": 90,
        "daniel": 85,
        "bob": 78
    }
    return{
        "name": name,
        "score": scores.get(name)
    }

class Student(BaseModel):
    name: str
    score: int

@app.post("/student")
def create_student(student: Student):
    return{
        "message": "Student created successfully",
        "student": student.name,
        "score": student.score
    }

class PredictionInput(BaseModel):
    value: float

@app.post("/predict")
def predict(data: PredictionInput):
    result = data.value * 2  # 假設的預測邏輯

    return{
        "input": data.value,
        "prediction": result
    }

@app.get("/user/{id}")
def get_user(id: int):
    return {"user_id": id}

@app.get("/products/{products_id}")
def get_product(products_id: int, quantity: int = 1):
    return {"product_id": products_id, "quantity": quantity}

