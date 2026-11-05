from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
# Ajout de ListProperty pour gérer proprement la couleur dynamique
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, BooleanProperty, ListProperty

class AddTaskPopup(Popup):
    """Fenêtre pop-up pour ajouter une tâche avec gestion des boutons radio."""
    def __init__(self, add_callback, **kwargs):
        super().__init__(**kwargs)
        self.add_callback = add_callback
        self.selected_priority = "Normal"  # Valeur par défaut

    def on_checkbox_active(self, checkbox, value, priority_name):
        """Met à jour la priorité sélectionnée lorsque l'utilisateur clique sur un bouton radio."""
        if value:
            self.selected_priority = priority_name

    def submit_task(self):
        """Récupère les champs et déclenche l'ajout."""
        title = self.ids.popup_title_input.text.strip()
        description = self.ids.popup_desc_input.text.strip()
        
        if title:
            self.add_callback(title, description, self.selected_priority)
            self.dismiss()

class TaskItem(BoxLayout):
    """Composant visuel représentant une ligne de tâche unique."""
    task_id = NumericProperty(0)
    task_title = StringProperty("")
    description = StringProperty("")
    priority = StringProperty("Normal")
    created_at = StringProperty("")
    is_completed = BooleanProperty(False)
    delete_callback = ObjectProperty(None)
    done_callback = ObjectProperty(None)
    
    # Propriété de couleur réactive pour le rectangle indicateur
    indicator_color = ListProperty([0.2, 0.7, 0.3, 1])

    def __init__(self, task_id, title, description, priority, created_at, completed, delete_callback, done_callback, **kwargs):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.task_title = f"[s]{title}[/s]" if completed else title
        self.description = description
        self.priority = priority
        self.created_at = created_at
        self.is_completed = completed
        self.delete_callback = delete_callback
        self.done_callback = done_callback

        # Détermine la couleur du rectangle selon la priorité reçue du serveur
        prio = self.priority.strip() if self.priority else "Normal"
        if prio == "Très important":
            self.indicator_color = [0.9, 0.2, 0.2, 1]  # Rouge vif
        elif prio == "Important":
            self.indicator_color = [0.9, 0.7, 0.1, 1]  # Jaune / Orange
        else:
            self.indicator_color = [0.2, 0.7, 0.3, 1]  # Vert (Normal)