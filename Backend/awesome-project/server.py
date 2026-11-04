# Importation des outils nécessaires depuis FastAPI
from fastapi import FastAPI, HTTPException
# Importation de BaseModel de Pydantic pour valider la structure des données reçues et envoyées
from pydantic import BaseModel
# Importation de List pour typer les listes de données
from typing import List
# Importation de datetime pour récupérer la date et l'heure actuelles du serveur
from datetime import datetime

# Initialisation de l'application FastAPI avec un titre personnalisé
app = FastAPI(title="To-Do List API")

# Modèle de données pour une tâche complète (envoyée par le serveur)
class Task(BaseModel):
    id: int               # Identifiant unique de la tâche
    title: str            # Libellé / contenu de la tâche
    completed: bool = False # État de la tâche (vrai si terminée, faux sinon, par défaut faux)
    created_at: str       # Date et heure de création au format texte

# Modèle de données pour la création d'une tâche (reçu du client Kivy)
class TaskCreate(BaseModel):
    title: str            # Seul le titre est nécessaire lors de la création par l'utilisateur

# Base de données temporaire stockée en mémoire vive (liste Python)
db_tasks: List[Task] = []

# Route HTTP GET pour récupérer la liste de toutes les tâches
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return db_tasks  # Renvoie toute la liste des tâches au client

# Route HTTP POST pour ajouter une nouvelle tâche
@app.post("/tasks", response_model=Task)
def create_task(task_in: TaskCreate):
    # Génération d'un nouvel ID unique : trouve le max des ID existants + 1, ou 1 si la liste est vide
    new_id = max([t.id for t in db_tasks], default=0) + 1
    
    # Récupération de la date et de l'heure actuelles formatées en français (ex: "04/11/2026 15:30")
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Création de l'objet Task complet
    new_task = Task(
        id=new_id, 
        title=task_in.title, 
        completed=False, 
        created_at=current_date
    )
    
    # Ajout de la nouvelle tâche dans notre base de données en mémoire
    db_tasks.append(new_task)
    return new_task  # Renvoie la tâche créée au client

# Route HTTP PATCH pour basculer l'état d'une tâche (terminée <-> non terminée)
@app.patch("/tasks/{task_id}/toggle", response_model=Task)
def toggle_task(task_id: int):
    # Recherche de la tâche correspondante grâce à son ID
    task = next((t for t in db_tasks if t.id == task_id), None)
    # Si la tâche n'existe pas, on renvoie une erreur HTTP 404 (Non trouvé)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    # Inverse l'état actuel de completed (si c'est True ça devient False, et inversement)
    task.completed = not task.completed
    return task  # Renvoie la tâche mise à jour

# Route HTTP DELETE pour supprimer une tâche spécifique par son ID
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global db_tasks  # Indique qu'on modifie la variable globale de la base de données
    # Recherche de la tâche
    task = next((t for t in db_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    # Filtre la liste pour garder toutes les tâches SAUF celle qui a cet ID (ce qui la supprime)
    db_tasks = [t for t in db_tasks if t.id != task_id]
    return {"message": "Tâche supprimée avec succès"}