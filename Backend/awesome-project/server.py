from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="To-Do List API Pro")

# Modèle de données pour une tâche complète
class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    priority: str = "Normal"  # Stocke "Normal", "Important" ou "Très important"
    completed: bool = False
    created_at: str

# Modèle de données pour la création d'une tâche
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: str = "Normal"

db_tasks: List[Task] = []

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return db_tasks

@app.post("/tasks", response_model=Task)
def create_task(task_in: TaskCreate):
    new_id = max([t.id for t in db_tasks], default=0) + 1
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    new_task = Task(
        id=new_id, 
        title=task_in.title, 
        description=task_in.description,
        priority=task_in.priority, # Enregistre bien la priorité reçue
        completed=False, 
        created_at=current_date
    )
    db_tasks.append(new_task)
    return new_task

@app.patch("/tasks/{task_id}/toggle", response_model=Task)
def toggle_task(task_id: int):
    task = next((t for t in db_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    task.completed = not task.completed
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global db_tasks
    task = next((t for t in db_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    db_tasks = [t for t in db_tasks if t.id != task_id]
    return {"message": "Tâche supprimée avec succès"}