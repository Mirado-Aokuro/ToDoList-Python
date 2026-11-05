import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.lang import Builder
from ui_components import AddTaskPopup, TaskItem

# Chargement explicite du fichier de design .kv contenant les règles graphiques
Builder.load_file("todostyle.kv")

# URL de base de notre API FastAPI (Backend)
API_URL = "http://127.0.0.1:8000/tasks"


# CONTENEUR PRINCIPAL DE L'INTERFACE
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        """Initialise la disposition principale de l'application."""
        # Appel obligatoire du constructeur parent (BoxLayout) pour configurer les propriétés de base
        super(MainLayout, self).__init__(**kwargs)
        
        # Planifie le chargement des tâches 0.3 seconde après le démarrage.
        # Cela garantit que l'interface et ses IDs sont totalement construits avant d'interagir avec eux.
        Clock.schedule_once(lambda dt: self.fetch_tasks(), 0.3)

    def fetch_tasks(self):
        """Récupère la liste des tâches depuis le serveur FastAPI et met à jour l'affichage."""
        try:
            # Effectue une requête HTTP GET vers l'API
            response = requests.get(API_URL, timeout=2)
            if response.status_code == 200:
                # Vérifie que l'ID du conteneur de tâches existe bien dans le fichier .kv avant de continuer
                if 'tasks_container' in self.ids:
                    container = self.ids.tasks_container
                    container.clear_widgets() # Nettoie l'affichage pour éviter les doublons
                    
                    # Parcourt chaque tâche reçue au format JSON
                    for task in response.json():
                        # Crée un composant visuel représentant la tâche
                        item = TaskItem(
                            task_id=task['id'], 
                            title=task['title'], 
                            description=task.get('description', ''),
                            priority=task.get('priority', 'Normal'),
                            created_at=task['created_at'],
                            completed=task['completed'],
                            delete_callback=self.delete_task,
                            done_callback=self.toggle_task
                        )
                        # Ajoute la tâche dans la liste visuelle de l'écran
                        container.add_widget(item)
        except requests.exceptions.RequestException:
            print("Erreur de connexion au serveur FastAPI")

    def open_add_task_popup(self):
        """Ouvre la fenêtre pop-up de création d'une nouvelle tâche."""
        # Instancie la pop-up en lui transmettant une fonction de rappel (callback)
        popup = AddTaskPopup(add_callback=self.send_new_task_to_api)
        popup.open()

    def send_new_task_to_api(self, title, description, priority):
        """Envoie une nouvelle tâche au serveur backend via une requête POST."""
        if title:
            # Prépare les données (payload) à envoyer au format JSON
            payload = {
                "title": title,
                "description": description,
                "priority": priority
            }
            try:
                response = requests.post(API_URL, json=payload, timeout=2)
                if response.status_code == 200:
                    self.fetch_tasks() # Rafraîchit l'affichage de la liste après l'ajout réussi
            except requests.exceptions.RequestException:
                print("Impossible d'ajouter la tâche")

    def toggle_task(self, task_id):
        """Bascule l'état d'une tâche (terminée ou en cours) via une requête PATCH."""
        try:
            response = requests.patch(f"{API_URL}/{task_id}/toggle", timeout=2)
            if response.status_code == 200:
                self.fetch_tasks() # Rafraîchit la liste pour refléter le changement
        except requests.exceptions.RequestException:
            print("Impossible de modifier la tâche")

    def delete_task(self, task_id):
        """Supprime une tâche spécifique du serveur via son ID (requête DELETE)."""
        try:
            response = requests.delete(f"{API_URL}/{task_id}", timeout=2)
            if response.status_code == 200:
                self.fetch_tasks() # Rafraîchit la liste après suppression
        except requests.exceptions.RequestException:
            print("Impossible de supprimer la tâche")


# 3. LANCEMENT DE L'APPLICATION KIVY

class TodoApp(App):
    """Classe principale de l'application Kivy."""
    def build(self):
        """Définit le titre de la fenêtre et retourne le layout principal."""
        self.title = "To-Do List Cloud"
        return MainLayout()

if __name__ == '__main__':
    # Point d'entrée standard pour exécuter l'application
    TodoApp().run()