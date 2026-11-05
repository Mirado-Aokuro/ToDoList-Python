import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.lang import Builder
from ui_components import AddTaskPopup, TaskItem

# Chargement du fichier de design global
Builder.load_file("todostyle.kv")

API_URL = "http://127.0.0.1:8000/tasks"

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        # Appel obligatoire du constructeur parent pour que Kivy construise les IDs du .kv
        super(MainLayout, self).__init__(**kwargs)
        
        # Planifie le chargement des tâches légèrement après pour garantir que les IDs sont chargés
        Clock.schedule_once(lambda dt: self.fetch_tasks(), 0.3)

    def fetch_tasks(self):
        """Récupère les tâches depuis FastAPI et les affiche."""
        try:
            response = requests.get(API_URL, timeout=2)
            if response.status_code == 200:
                # Vérifie que l'ID existe bien avant de l'utiliser pour éviter tout crash
                if 'tasks_container' in self.ids:
                    container = self.ids.tasks_container
                    container.clear_widgets()
                    
                    for task in response.json():
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
                        container.add_widget(item)
        except requests.exceptions.RequestException:
            print("Erreur de connexion au serveur FastAPI")

    def open_add_task_popup(self):
        """Ouvre la pop-up de création de tâche."""
        popup = AddTaskPopup(add_callback=self.send_new_task_to_api)
        popup.open()

    def send_new_task_to_api(self, title, description, priority):
        """Envoie la nouvelle tâche au serveur avec sa priorité."""
        if title:
            payload = {
                "title": title,
                "description": description,
                "priority": priority
            }
            try:
                response = requests.post(API_URL, json=payload, timeout=2)
                if response.status_code == 200:
                    self.fetch_tasks()
            except requests.exceptions.RequestException:
                print("Impossible d'ajouter la tâche")

    def toggle_task(self, task_id):
        """Bascule l'état (terminé/en cours) de la tâche."""
        try:
            response = requests.patch(f"{API_URL}/{task_id}/toggle", timeout=2)
            if response.status_code == 200:
                self.fetch_tasks()
        except requests.exceptions.RequestException:
            print("Impossible de modifier la tâche")

    def delete_task(self, task_id):
        """Supprime une tâche par son ID."""
        try:
            response = requests.delete(f"{API_URL}/{task_id}", timeout=2)
            if response.status_code == 200:
                self.fetch_tasks()
        except requests.exceptions.RequestException:
            print("Impossible de supprimer la tâche")

class TodoApp(App):
    def build(self):
        self.title = "To-Do List Cloud - Pro"
        return MainLayout()

if __name__ == '__main__':
    TodoApp().run()