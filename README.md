# VisuValideMultiCriteriaMatching

Plugin de visualisation des résultats d'appariement multi-critères pour le logiciel QGIS.

# Introduction

Le projet [MultiCriteriaMatching](https://github.com/IGNF/MultiCriteriaMatching) permet de réaliser un appariement de données multicritères 
basé sur la théorie des fonctions de croyances. L’algorithme d’appariement se base sur un jeu de données de référence et sur un jeu de données 
de comparaison donnant ainsi une direction à l’appariement (pour chaque donnée du jeu de référence, l’algorithme recherche les données 
homologues et candidates dans le jeu de comparaison). Notons que le jeu de données de référence peut être un jeu de données faisant autorité 
ou un jeu de données collaboratif.

Ce plugIn permet de visualiser les objets de référence et les objets de comparaison candidats. 
Si l'appariement a été trouvé ou s'il y a indécision, l'information est signalée. Les objets de référence sont affichés un par un. 
Ce plugIn permet de réaliser la validation manuelle plus facilement.

