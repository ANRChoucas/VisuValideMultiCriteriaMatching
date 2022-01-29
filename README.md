# VisuValideMultiCriteriaMatching

Plugin de visualisation des résultats d'appariement multi-critères pour le logiciel QGIS.

# Introduction

Le projet [MultiCriteriaMatching](https://github.com/IGNF/MultiCriteriaMatching) permet de réaliser un appariement de données multicritères 
basé sur la théorie des fonctions de croyances. L’algorithme d’appariement se base sur un jeu de données de référence et sur un jeu de données 
de comparaison donnant ainsi une direction à l’appariement (pour chaque donnée du jeu de référence, l’algorithme recherche les données 
homologues et candidates dans le jeu de comparaison). Notons que le jeu de données de référence peut être un jeu de données faisant autorité 
ou un jeu de données collaboratif.

Ce plugIn permet de visualiser les objets de référence et les objets de comparaison candidats et les liens d'appariement calculés avec 
l'algorithme d'appariement *MultiCriteriaMatching*. 
Si l'appariement a été trouvé ou s'il y a indécision, l'information est visible dans QGIS grâce au plugin. Les objets de référence sont affichés un par un. 
Ce plugIn permet de réaliser la validation manuelle directement dans un fichier dédié.


# Installation

VisuValideMultiCriteriaMatching est un plugin pour le logiciel QGis. Il est donc nécessaire que ce dernier soit installé sur l’ordinateur. 
QGis peut être téléchargé gratuitement via l’URL suivant : http://www.qgis.org/fr/site/

Le plugin a été testé avec succès sur les versions 3.22 de QGis. 

Le code source du plugIn doit être installé dans le répertoire des plugins de Qgis:
* sous windows: C:/Utilisateurs/glagaffe/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins
* sous linux: /home/glagaffe/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

# Screenshot

Commencer par charger le fichier de résultat en sortie de l'algorithme **MultiCriteriaMatching**

![GitHub Logo](/img/PlugInVisuMatchingMultiCrit_VersionChoucas.png)