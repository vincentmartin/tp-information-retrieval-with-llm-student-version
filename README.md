# TP Recherche d'Information

## Avant de démarrer

Forker le projet dans votre espace github avant de commencer

## TP1. - Recherche d'information _classique_

Dans ce TP, vous allez mettre en oeuvre des techniques de recherche d'information classiques : 
- Construction d'un index inversé
- Calcul des pondérations des mots dans les documents avec la méthode _TF-IDF_
- Implémentation du modèle booléen
- Implémentation du modèle vectoriel

## Données

Les données sont un ensemble de 60 livres au format texte (.txt) d'[Henry Rider Haggard ](https://fr.wikipedia.org/wiki/Henry_Rider_Haggard).

## Exercices

Répondre aux questions dans le notebook [1-Recherche d'information classique.ipynb](./1-Recherche%20d'information%20classique.ipynb).

**Attention : Ne pas modifier les autres fichiers !!**

## Notation et objectif

L'objectif est d'obtenir un score de 5/5 sur tous les tests. 

La notation prendra également en compte la qualité de votre code et son optimisation.

## TP2 - Recherche d'information _sémantique_

Dans ce TP, vous allez mettre en oeuvre des techniques de recherche sémantique pour fournir des réponses plus pertinentes aux utilisateurs. Vous allez en particulier : 
- Mettre en oeuvre [langchain](https://www.langchain.com/) pour construire l'application exploitant des LLMs
- Lire et découper les documents en paragraphes
- Convertir les paragraphes en embeddings en utilisant un modèle existant issu de [Huggingface](https://huggingface.co/models)
- Indexer les données dans le _vector store_ [ChromaDB](https://www.trychroma.com/) et y rechercher des informations
- Mettre en oeuvre un chatbot grâce aux techniques de Retrieval Augmented Generation (RAG) sur vos propres données !!


## Données

Les données sont un ensemble de 2225 articles de _BBC News_ au format texte issus de https://www.kaggle.com/c/learn-ai-bbc.

## Exercices

Dérouler le notebook [2-Recherche d'information sémantique.ipynb](./2-Recherche%20d'information%20sémantique.ipynb) et répondre aux questions posées.


## Notation et objectif

L'objectif est de répondre à toutes les questions du TP.

La notation prendra également en compte la qualité de votre code et son optimisation.


# Rendu des 2 TPs

Vous devez rendre votre TP sous la forme d'un lien github avec vos TP complétés ou en déposant vos 2 notebooks sur Moodle.