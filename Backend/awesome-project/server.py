from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# INITIALISATION DE L'APPLICATION FASTAPI

# Crée l'instance de l'application avec un titre personnalisé pour la documentation automatique (/docs)
app = FastAPI(title="To-Do List API Pro")


# DÉFINITION DES MODÈLES DE DONNÉES (PYDANTIC)

class Task(BaseModel):
    """
    Modèle représentant une tâche complète enregistrée dans la 'base de données'.
    Contient l'ID, le titre, la description, la priorité, l'état et la date de création.
    """
    id: int
    title: str
    description: Optional[str] = ""
    priority: str = "Normal"  # Stocke "Normal", "Important" ou "Très important"
    completed: bool = False
    created_at: str


class TaskCreate(BaseModel):
    """
    Modèle utilisé lors de la création d'une tâche (requête POST).
    L'utilisateur envoie uniquement ces informations, le serveur génère le reste (ID, date, etc.).
    """
    title: str
    description: Optional[str] = ""
    priority: str = "Normal"


# "Base de données" temporaire stockée en mémoire vive sous forme de liste Python
db_tasks: List[Task] = []

# ENDPOINTS REST API (ROUTES DU SERVEUR)

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    """
    Route GET : Récupère et retourne la liste de toutes les tâches enregistrées.
    """
    return db_tasks


@app.post("/tasks", response_model=Task)
def create_task(task_in: TaskCreate):
    """
    Route POST : Crée une nouvelle tâche à partir des données reçues,
    génère un ID unique et enregistre la date/heure actuelle.
    """
    # Génère un nouvel ID incrémenté automatiquement (prend le max actuel + 1, ou 1 si la liste est vide)
    new_id = max([t.id for t in db_tasks], default=0) + 1
    
    # Récupère la date et l'heure actuelles au format lisible "JJ/MM/AAAA HH:MM"
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Instancie l'objet Task complet
    new_task = Task(
        id=new_id, 
        title=task_in.title, 
        description=task_in.description,
        priority=task_in.priority, # Enregistre bien la priorité reçue du frontend
        completed=False,           # Par défaut, une nouvelle tâche n'est pas complétée
        created_at=current_date
    )
    
    # Ajoute la tâche dans notre liste en mémoire
    db_tasks.append(new_task)
    return new_task


@app.patch("/tasks/{task_id}/toggle", response_model=Task)
def toggle_task(task_id: int):
    """
    Route PATCH : Bascule l'état d'une tâche (passe de complétée à non complétée et inversement)
    en recherchant la tâche par son ID.
    """
    # Recherche la tâche correspondante dans la liste
    task = next((t for t in db_tasks if t.id == task_id), None)
    
    # Si la tâche n'existe pas, retourne une erreur HTTP 404
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    # Inverse l'état booléen de la propriété 'completed'
    task.completed = not task.completed
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """
    Route DELETE : Supprime définitivement une tâche de la liste en fonction de son ID.
    """
    global db_tasks  # Permet de modifier la variable globale de la liste
    
    # Vérifie si la tâche existe avant de la supprimer
    task = next((t for t in db_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    # Filtre la liste pour exclure la tâche ciblée
    db_tasks = [t for t in db_tasks if t.id != task_id]
    return {"message": "Tâche supprimée avec succès"}