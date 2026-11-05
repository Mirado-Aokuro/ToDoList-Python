from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, BooleanProperty, ListProperty

# 1. POP-UP D'AJOUT DE TÂCHE

class AddTaskPopup(Popup):
    """Fenêtre modale (pop-up) permettant de saisir une nouvelle tâche et de choisir sa priorité."""
    
    def __init__(self, add_callback, **kwargs):
        """Initialise la pop-up avec une fonction de rappel et une priorité par défaut."""
        super().__init__(**kwargs)
        self.add_callback = add_callback       # Fonction à appeler lors de la validation
        self.selected_priority = "Normal"        # Priorité sélectionnée par défaut

    def on_checkbox_active(self, checkbox, value, priority_name):
        """
        Met à jour la priorité sélectionnée lorsque l'utilisateur coche un bouton radio.
        'value' est un booléen (True si le bouton vient d'être coché, False sinon).
        """
        if value:
            self.selected_priority = priority_name

    def submit_task(self):
        """Récupère les champs de texte saisis et déclenche l'ajout de la tâche."""
        title = self.ids.popup_title_input.text.strip()
        description = self.ids.popup_desc_input.text.strip()
        
        # Vérifie que le titre n'est pas vide avant de valider
        if title:
            # Transmet les informations au fichier principal via le callback
            self.add_callback(title, description, self.selected_priority)
            self.dismiss()  # Ferme la fenêtre pop-up


# 2. LIGNE D'UNE TÂCHE INDIVIDUELLE

class TaskItem(BoxLayout):
    """Composant visuel représentant une carte de tâche unique dans la liste déroulante."""
    
    # Définition des propriétés Kivy réactives
    task_id = NumericProperty(0)
    task_title = StringProperty("")
    description = StringProperty("")
    priority = StringProperty("Normal")
    created_at = StringProperty("")
    is_completed = BooleanProperty(False)
    delete_callback = ObjectProperty(None)
    done_callback = ObjectProperty(None)
    
    # Propriété de couleur réactive pour le petit rectangle indicateur à gauche
    indicator_color = ListProperty([0.2, 0.7, 0.3, 1])  # Vert par défaut

    def __init__(self, task_id, title, description, priority, created_at, completed, delete_callback, done_callback, **kwargs):
        """Initialise une ligne de tâche avec toutes ses données et attributs graphiques."""
        super().__init__(**kwargs)
        self.task_id = task_id
        # Si la tâche est complétée, on applique la balise Kivy [s] pour barrer le texte
        self.task_title = f"[s]{title}[/s]" if completed else title
        self.description = description
        self.priority = priority
        self.created_at = created_at
        self.is_completed = completed
        self.delete_callback = delete_callback
        self.done_callback = done_callback

        # Nettoie les espaces superflus de la priorité reçue du serveur
        prio = self.priority.strip() if self.priority else "Normal"
        
        # Attribue la couleur du rectangle indicateur selon la priorité exacte
        if prio == "Très important":
            self.indicator_color = [0.9, 0.2, 0.2, 1]  # Rouge vif
        elif prio == "Important":
            self.indicator_color = [0.9, 0.7, 0.1, 1]  # Jaune / Orange
        else:
            self.indicator_color = [0.2, 0.7, 0.3, 1]  # Vert (Normal)