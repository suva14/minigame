# minigame# **README - Jeu de Réflexes**

## **Description**
Un jeu de réaction développé en Python avec `pygame`, où le joueur doit interagir rapidement avec des éléments pour marquer des points. Les scores et statistiques des joueurs sont enregistrés dans des fichiers CSV, analysés et visualisés à l'aide de `matplotlib` et `pandas`.

## **Classes Principales**

### **1. `Don`**
- Représente les objets à capturer (position, couleur, vitesse).
- Méthodes : déplacement, dessin, détection de collision.

### **2. `Game`**
- Gère la logique du jeu : score, erreurs, streaks, sauvegarde des résultats dans des fichiers CSV.
- On peut aussi pauser.

### **3. `Menu` et `Leaderboard`**
- `Menu` : navigation entre les options (jouer, quitter, leaderboard).
- `Leaderboard` : affiche les scores des meilleurs joueurs.

### **4. `NameInput`**
- Permet au joueur de saisir son nom avant une partie.

## **Visualisations**
Les fichiers CSV de chaque joueur sont utilisés pour produire les plots suivants :
1. **Score vs Temps de jeu** :
   - Montre la performance du joueur au fil des parties.
2. **Erreurs cumulées par joueur** :
   - Compare les erreurs totales entre les joueurs.
3. **Nombre de clics vs Score** :
   - Analyse si plus de clics conduit à de meilleurs scores.

## **Fichiers CSV**
- Un fichier par joueur (`<nom>.csv`).
- **Colonnes** : Date, Score, Meilleur Streak, Temps de jeu, Nombre de clics, Erreurs.
