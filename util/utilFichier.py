#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions de lecture du fichier

"""
import csv

def entete(uriResultat):
    
    DISTANCE_NOM = []
    CRITERE_SEUIL = []
    TYPE_GEOM = ''
    seuilIndecision = -1
    
    # On lit les entetes du fichier
    with open(uriResultat, 'r') as file:
        entete = 0
        for line in file:
            entete = entete + 1

            if entete == 2:
                # DISTANCES
                # 
                tab = line.split(":")
                tabdist = tab[1].strip(' ').split(',')
                    
                for i in range(len(tabdist)):
                    if tabdist[i] != None and tabdist[i].strip() != '':
                        DISTANCE_NOM.append(tabdist[i].strip(' ').strip('\n'))
                #print (self.DISTANCE_NOM)
                
            if entete == 3:
                # ATTRIBUTS
                line.split(":")
                
                    
            elif entete == 4:
                
                tab = line.split(":")
                seuilIndecision = float(tab[1].strip(' '))
            
            elif entete == 5:
                    
                tab = line.split(":")
                tabdist = tab[1].strip(' ').split('],')
                    
                for i in range(len(tabdist)):
                    if tabdist[i] != None and tabdist[i].strip() != '':
                        tab = tabdist[i].strip(' ').strip('\n').replace(']','')[1:]
                        # print (str(tab))
                        seuils = tab.split(',')
                        # print (seuils)
                        CRITERE_SEUIL.append(seuils)
                # print (self.CRITERE_SEUIL)
                
            elif entete == 6:
                # type de la géométrie à partir de la deuxième ligne 
                # split
                tab = line.split(":")
                typeGeom = tab[1].strip(' ').strip('\n')
                # print ('**' + typeGeom + '**')
                    
                if typeGeom == 'POINT':
                    TYPE_GEOM = 'Point'
                if typeGeom == 'LINESTRING':
                    TYPE_GEOM = 'Linestring'
                if typeGeom == 'POLYGON':
                    TYPE_GEOM = 'Polygon'
                if typeGeom == 'MULTILINESTRING':
                    TYPE_GEOM = 'MultiLinestring'
                if typeGeom == 'MULTIPOINT':
                    TYPE_GEOM = 'MultiPoint'
                if typeGeom == 'MULTIPOLYGON':
                    TYPE_GEOM = 'MultiPolygon'
                    
                    # print (self.TYPE_GEOM)
                    
            elif entete > 6:
                break
        
        file.close()
    
    return (DISTANCE_NOM, TYPE_GEOM, CRITERE_SEUIL, seuilIndecision)


def getLignePrec(uriResultat, currId):
    
    id = -1
    idref = -1
    
    with open(uriResultat, 'r') as file:
        noligne = 0
        
        for line in file:
            noligne = noligne + 1
            
            if noligne > 8:
                # split
                tab = line.split(";")
                if len(tab) < 2:
                    tab = line.split(",")
                
                idref = tab[0].replace('"', '')
                
                if currId == "-1":
                    id = idref
                    break
                else: 
                    if currId == idref:
                        return id
                    id = idref
                
        file.close()
    
    return id


def getLigneSuiv(uriResultat, currId):
    
    id = -1
    stop = False
    idref = -1
    
    with open(uriResultat, 'r') as file:
        noligne = 0
        
        for line in file:
            noligne = noligne + 1
            
            if noligne > 8:
                # split
                tab = line.split(";")
                if len(tab) < 2:
                    tab = line.split(",")
                    
                idref = tab[0].replace('"', '')
                
                if stop and currId != idref:
                    id = idref
                    break
                    
                if currId == "-1":
                    id = idref
                    break
                        
                else: 
                    if currId == idref:
                        stop = True
                
        file.close()

    return id


def getsep(uriResultat):
    with open(uriResultat, 'r') as file:
        noligne = 0
        
        for line in file:
            noligne = noligne + 1
            
            if noligne > 8:
                # split
                tab = line.split(";")
                if len(tab) < 2:
                    return ","
                else:
                    return ";"
        file.close()
    
    return ";"


def getRefInfo(uriResultat, currId):
    sep = getsep(uriResultat)
    with open(uriResultat, 'r') as file:
        reader = csv.reader(file, quotechar='"', delimiter=sep,
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)
        noligne = 0
        for tab in reader:
            noligne = noligne + 1
            if noligne > 8:
                idref = tab[0]
                if currId == idref:
                    return (tab[1], tab[5])
        file.close()
    return None
    

def getCandidat(uriResultat, currId, NOM_DISTANCES):
    candList = []
    sep = getsep(uriResultat)
    with open(uriResultat, 'r') as file:
        reader = csv.reader(file, quotechar='"', delimiter=sep,
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)
        noligne = 0
        for tab in reader:
            
    
    #with open(uriResultat, 'r') as file:
    #    noligne = 0
    #    for line in file:
            noligne = noligne + 1
            
            if noligne > 8:
                # split
                #tab = line.split(";")
                idref = tab[0]
                    
                if currId == idref:
                    cand = dict()
                    
                    cand['idref'] = tab[0]     # 'id' ref
                    cand['nomref'] = tab[1]     # 'id' ref
                    cand['uriref'] = tab[5]     # 'id' ref
                    
                    cand['num'] = tab[2]    # 'num'
                    cand['id'] = tab[3]     # 'id'
                    cand['nom'] = tab[4]    # 'nom'
                    
                    # Attributs supplémentaires
                    cand['uri'] = tab[6]
                        
                    cand['pign1'] = tab[10]
                    cand['pign2'] = tab[11]
                    cand['decision'] = tab[12]
                        
                    cand[NOM_DISTANCES[0]] = tab[7]
                    cand[NOM_DISTANCES[1]] = tab[8]
                    cand[NOM_DISTANCES[2]] = tab[9]
                        
                    cand['geomref'] = tab[13]
                    cand['geomcomp'] = tab[14]
                        
                    candList.append(cand)
        file.close()
    return candList


def getLabelResultat(candList):
    nbApp = 0
    nbNonApp = 0
    nbIndecis = 0
    labelRes = ''
    geom1 = None
    geom2 = None
    
    for i in range(len(candList)):
        candidat = candList[i]

        isNA = False
        if candidat['nom'] == 'NA':
            isNA = True

        # decision et resultat
        if (isNA and candidat['decision'] == 'true'):
            nbNonApp = nbNonApp + 1
						
        if (not isNA and candidat['decision'] == 'true'):
            nbApp = nbApp + 1
            labelRes = candidat['id']
            geom1 = candidat['geomref']
            geom2 = candidat['geomcomp']
						
        if (isNA and candidat['decision'] == 'indécis'):
            nbIndecis = nbIndecis + 1
						
    if nbIndecis > 0:
        return ('INDECIS')
    elif nbNonApp > 0:
        return ("Pas d'appariement")
    elif nbApp > 0:
        return ("Appariement", labelRes, geom1, geom2)
    else:
        return ('Inconnu')


def lienappariement(uriResultat, NOM_DISTANCES):
    LINKS = []
    sep = getsep(uriResultat)
    with open(uriResultat, 'r') as file:
        noligne = 0
        idrefold = '-1'
        for line in file:
            if noligne > 7:
                tab = line.split(sep)
                idref = tab[0].replace('"', '')
                if idref == idrefold:
                    continue
                
                candList = getCandidat(uriResultat, idref, NOM_DISTANCES)
                labels = getLabelResultat(candList)
                if 'Appariement' == labels[0]:
                    LINKS.append((idref, labels[1], labels[2], labels[3]))
                    
                idrefold = idref
                #break
            
            noligne = noligne + 1    
        file.close()
    
    return LINKS