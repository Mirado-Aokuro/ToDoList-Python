# Importation de la bibliothèque requests pour effectuer des requêtes HTTP vers l'API FastAPI
import requests
# Importation de la classe principale de l'application Kivy
from kivy.app import App
# Importation du conteneur BoxLayout pour organiser les éléments graphiques
from kivy.uix.boxlayout import BoxLayout
# Importation de Clock pour planifier l'exécution de fonctions (ex: charger les tâches au démarrage)
from kivy.clock import Clock
# Importation des types de propriétés Kivy pour lier dynamiquement le code Python au design .kv
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, BooleanProperty
# Importation de Builder pour charger manuellement notre fichier de design .kv
from kivy.lang import Builder

# Chargement explicite du fichier de design de l'interface
Builder.load_file("todostyle.kv")

# URL de base de notre API FastAPI distante ou locale
API_URL = "http://127.0.0.1:8000/tasks"

# Classe représentant une ligne de tâche individuelle dans l'interface
class TaskItem(BoxLayout):
    # Déclaration des propriétés Kivy liées aux variables du fichier .kv
    task_id = NumericProperty(0)        # ID numérique de la tâche
    task_title = StringProperty("")     # Titre de la tâche
    created_at = StringProperty("")     # Date de création
    is_completed = BooleanProperty(False) # Indique si la tâche est finie ou non
    delete_callback = ObjectProperty(None) # Référence vers la fonction de suppression
    done_callback = ObjectProperty(None)   # Référence vers la fonction de validation (Done)

    # Constructeur personnalisé pour initialiser les valeurs de la tâche
    def __init__(self, task_id, title, created_at, completed, delete_callback, done_callback, **kwargs):
        super().__init__(**kwargs)
        self.task_id = task_id
        # Si la tâche est complétée, on applique une balise Kivy [s] pour la barrer visuellement
        self.task_title = f"[s]{title}[/s]" if completed else title  
        self.created_at = created_at
        self.is_completed = completed
        self.delete_callback = delete_callback
        self.done_callback = done_callback

# Classe principale correspondant au conteneur global défini dans le fichier .kv (<MainLayout>)
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Planifie l'appel de fetch_tasks 0.5 seconde après le lancement pour laisser l'UI s'initialiser
        Clock.schedule_once(lambda dt: self.fetch_tasks(), 0.5)

    # Méthode pour récupérer la liste des tâches depuis l'API FastAPI
    def fetch_tasks(self):
        try:
            # Envoi d'une requête HTTP GET au serveur
            response = requests.get(API_URL, timeout=2)
            if response.status_code == 200:
                # Récupère le conteneur vertical des tâches grâce à son ID défini dans le .kv
                container = self.ids.tasks_container
                container.clear_widgets() # Nettoie l'affichage actuel pour éviter les doublons
                
                # Boucle sur chaque tâche reçue du serveur au format JSON
                for task in response.json():
                    # Crée un composant visuel TaskItem pour chaque tâche
                    item = TaskItem(
                        task_id=task['id'], 
                        title=task['title'], 
                        created_at=task['created_at'],
                        completed=task['completed'],
                        delete_callback=self.delete_task,
                        done_callback=self.toggle_task
                    )
                    # Ajoute l'élément visuel dans le conteneur de la liste
                    container.add_widget(item)
        except requests.exceptions.RequestException:
            print("Erreur de connexion au serveur FastAPI")

    # Méthode pour ajouter une nouvelle tâche via l'API
    def add_task(self):
        # Récupère le champ de texte saisi par l'utilisateur via son ID dans le .kv
        task_input = self.ids.task_input
        title = task_input.text.strip() # .strip() supprime les espaces inutiles au début et à la fin
        
        # Vérifie que le champ n'est pas vide
        if title:
            try:
                # Envoi d'une requête HTTP POST avec le titre de la tâche en JSON
                response = requests.post(API_URL, json={"title": title}, timeout=2)
                if response.status_code == 200:
                    task_input.text = ""  # Vide le champ de texte après l'ajout réussi
                    self.fetch_tasks()    # Rafraîchit la liste affichée à l'écran
            except requests.exceptions.RequestException:
                print("Impossible d'ajouter la tâche")

    # Méthode pour basculer l'état (terminé / en cours) d'une tâche
    def toggle_task(self, task_id):
        try:
            # Envoi d'une requête HTTP PATCH vers l'URL de bascule du serveur
            response = requests.patch(f"{API_URL}/{task_id}/toggle", timeout=2)
            if response.status_code == 200:
                self.fetch_tasks() # Rafraîchit l'affichage pour voir le texte barré
        except requests.exceptions.RequestException:
            print("Impossible de modifier la tâche")

    # Méthode pour supprimer une tâche
    def delete_task(self, task_id):
        try:
            # Envoi d'une requête HTTP DELETE au serveur avec l'ID de la tâche
            response = requests.delete(f"{API_URL}/{task_id}", timeout=2)
            if response.status_code == 200:
                self.fetch_tasks() # Rafraîchit la liste après la suppression
        except requests.exceptions.RequestException:
            print("Impossible de supprimer la tâche")

# Classe globale de l'application Kivy
class TodoApp(App):
    def build(self):
        self.title = "To-Do List Cloud"
        return MainLayout() # Retourne le layout principal pour affichage

# Point d'entrée du script : lance l'application si on exécute directement ce fichier
if __name__ == '__main__':
    TodoApp().run()