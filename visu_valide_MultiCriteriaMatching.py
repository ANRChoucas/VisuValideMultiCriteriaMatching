# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VisuValideMultiCriteriaMatching
                                 A QGIS plugin
                                 
 VisuValideMultiCriteriaMatching est un plugIn QGis pour valider l'appariement
                              -------------------
        begin                : 2018-07-09
        git sha              : $Format:%H$
        copyright            : (C) 2018 by IGN
        email                : marie-dominique.van-damme@ign.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QColor
from PyQt5 import QtGui
from PyQt5.QtWidgets import QTableWidgetItem

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsProject, QgsVectorLayer
from qgis.core import QgsGeometry, QgsFeature
from qgis.core import QgsFillSymbol, QgsSingleSymbolRenderer
from qgis.core import QgsField
from qgis.core import QgsPalLayerSettings


# Initialize Qt resources from file resources.py
from .resources import resources

# Import the code for the gui
from .gui.visu_resultat_dialog import VisuResultatDialog


import os.path
import os


class VisuValideMultiCriteriaMatching:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor."""
        
        # Save reference to the QGIS interface
        self.iface = iface
        
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        
        # Create the dialog (after translation) and keep reference
        self.pluginIsActive = False
        self.dockwidget = None

        # Declare instance attributes
        self.actions = []
        self.menu = "Visualisation et validation de l'appariement"
        
        # We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'VisuValideMultiCriteriaMatching')
        self.toolbar.setObjectName(u'VisuValideMultiCriteriaMatching')
        
        self.uriSettings = os.path.join(self.plugin_dir, 'settings.conf')


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar."""

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action
    

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/VisuValideMultiCriteriaMatching/img/match.png'
        self.add_action(
            icon_path,
            text = "Panneau de contrôle pour visualiser et valider l'appariement",
            callback = self.initPoussePousse,
            parent = self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                '&VisuValideMultiCriteriaMatching',
                action)
            self.iface.removeToolBarIcon(action)
        
        # remove the toolbar
        del self.toolbar
        
        # remove layer ?
        
    
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        self.pluginIsActive = False

        # On recharge pour repartir       
        #self.reload()

        # On supprime les layers de la fenêtre        
        self.vider()

        # On ferme
        self.dockwidget.close()
        
    
    def vider(self):
        
        # ----------------------------------------------------------------------------
        # supprime les layers
        if self.layerIGN != None:
            QgsMapLayerRegistry.instance().removeMapLayers( [self.layerIGN.id()] )
        if self.layerOSM != None:
            QgsMapLayerRegistry.instance().removeMapLayers( [self.layerOSM.id()] )


    def initPoussePousse(self):
        """Run method that performs all the real work"""
        
        if not self.pluginIsActive:
            
            self.pluginIsActive = True       
       
            if self.dockwidget == None:
                
                self.dockwidget = VisuResultatDialog()
                
                self.layerIGN = None
                self.layerOSM = None
                
                self.dockwidget.btPrec.setStyleSheet('color : black;font: 8pt MS Shell Dlg 2')
                self.dockwidget.btSuiv.setStyleSheet('color : black;font: 8pt MS Shell Dlg 2')
                self.dockwidget.currentId.setStyleSheet('color : black;font: 8pt MS Shell Dlg 2')
                self.dockwidget.fileResultat.setStyleSheet('color : black;font: 8pt MS Shell Dlg 2')
                
                self.dockwidget.btSuiv.clicked.connect(self.doSuivant)
                self.dockwidget.btPrec.clicked.connect(self.doPrecedent)
                self.dockwidget.currentId.setDisabled(True)
                self.dockwidget.currentId.setText("-1")
                
                self.dockwidget.btFermer.clicked.connect(self.onClosePlugin)
                self.dockwidget.btZoomGrille.clicked.connect(self.zoom)
                
                self.dockwidget.fileResultat.fileChanged.connect(self.importFichier)
                
                self.dockwidget.D1_T1.setText("0.4")
                self.dockwidget.D1_T2.setText("1.5")
                
                self.dockwidget.D2_T1.setText("2")
                self.dockwidget.D2_T2.setText("5")
                
                self.dockwidget.D3_T1.setText("0.2")
                self.dockwidget.D3_T2.setText("0.8")
                
                self.dockwidget.D4_T1.setText("1.5")
                self.dockwidget.D4_T2.setText("7")
                
        self.iface.mapCanvas().refresh()
                
        # show the dockwidget
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        self.dockwidget.show()
        
    
    def importFichier(self):
        
        # On supprime les layers car on va les recreer
        self.vider()
        
        # On charge le chemin du fichier de résultat
        self.uriGrille = self.dockwidget.fileResultat.filePath().strip()
        # print (uriGrille)
        
        # On ouvre le fichier pour le type de la géométrie et les distances
        self.NOM_DISTANCES = []
        self.TYPE_GEOM = ''
        
        n = 0
        with open(self.uriGrille, 'r') as file:
            entete = True
            ligne1 = True
            for line in file:
                if entete:
                    entete = False
                    
                    # split
                    tab = line.split(";")
                    
                    for i in range(len(tab)):
                        if tab[i] != None and tab[i].strip() != '':
                            n = n + 1
                    # n = len(tab)
                    nb_distance = n - 10
                    # print (nb_distance)
                    
                    for i in range (5, 5 + nb_distance):
                        self.NOM_DISTANCES.append(tab[i])
                    # print (NOM_DISTANCES)
                    
                else:
                    # type de la géométrie à partir de la deuxième ligne 
                    if ligne1:
                        ligne1 = False
                    else: 
                        # split
                        tab = line.split(";")
                        wktGeom = tab[n - 2]
                        
                        tabGeom = wktGeom.split("(")
                        typeGeom = tabGeom[0].strip()
                        # print (typeGeom +"--")
                        
                        if typeGeom == 'POINT':
                            self.TYPE_GEOM = 'Point'
                        if typeGeom == 'LINESTRING':
                            self.TYPE_GEOM = 'Linestring'
                        if typeGeom == 'POLYGON':
                            self.TYPE_GEOM = 'Polygon'
                        if typeGeom == 'MULTILINESTRING':
                            self.TYPE_GEOM = 'MultiLinestring'
                        if typeGeom == 'MULTIPOINT':
                            self.TYPE_GEOM = 'MultiPoint'
                        if typeGeom == 'MULTIPOLYGON':
                            self.TYPE_GEOM = 'MultiPolygon'
                        # print (self.TYPE_GEOM)
                        
                        break
        
        self.dockwidget.currentId.setText("-1")
        
        self.createLayerOSM()
        self.createLayerIGN()
        
        self.dockwidget.labelSeuil1.setEnabled(False)
        self.dockwidget.D1_T1.setEnabled(False)
        self.dockwidget.D1_T2.setEnabled(False)
        
        self.dockwidget.labelSeuil2.setEnabled(False)
        self.dockwidget.D2_T1.setEnabled(False)
        self.dockwidget.D2_T2.setEnabled(False)
        
        self.dockwidget.labelSeuil3.setEnabled(False)
        self.dockwidget.D3_T1.setEnabled(False)
        self.dockwidget.D3_T2.setEnabled(False)
        
        self.dockwidget.labelSeuil4.setEnabled(False)
        self.dockwidget.D4_T1.setEnabled(False)
        self.dockwidget.D4_T2.setEnabled(False)
        
        self.dockwidget.labelSeuil5.setEnabled(False)
        self.dockwidget.D5_T1.setEnabled(False)
        self.dockwidget.D5_T2.setEnabled(False)
        
        
        for i in range (len(self.NOM_DISTANCES)):
            if i == 0:
                self.dockwidget.labelSeuil1.setEnabled(True)
                self.dockwidget.D1_T1.setEnabled(True)
                self.dockwidget.D1_T2.setEnabled(True)
            if i == 1:
                self.dockwidget.labelSeuil2.setEnabled(True)
                self.dockwidget.D2_T1.setEnabled(True)
                self.dockwidget.D2_T2.setEnabled(True)
            if i == 2:
                self.dockwidget.labelSeuil3.setEnabled(True)
                self.dockwidget.D3_T1.setEnabled(True)
                self.dockwidget.D3_T2.setEnabled(True)
            if i == 3:
                self.dockwidget.labelSeuil4.setEnabled(True)
                self.dockwidget.D4_T1.setEnabled(True)
                self.dockwidget.D4_T2.setEnabled(True)
            if i == 4:
                self.dockwidget.labelSeuil5.setEnabled(True)
                self.dockwidget.D5_T1.setEnabled(True)
                self.dockwidget.D5_T2.setEnabled(True)
                
        
    def createLayerIGN(self):
        
        # ======================================================================================
        # Layer IGN
        self.layerIGN = QgsVectorLayer (self.TYPE_GEOM + "?crs=epsg:2154", "REF", "memory")
        
        # Style 
        props = {'color': '241,241,241,0', 'size':'1', 'color_border' : '255,0,0'}
        s = QgsFillSymbolV2.createSimple(props)
        self.layerIGN.setRendererV2(QgsSingleSymbolRendererV2(s))
                
        QgsProject.instance().addMapLayer(self.layerIGN)
        
        
        
    def createLayerOSM(self):

        # ======================================================================================
        # Layer OSM
        self.layerOSM = QgsVectorLayer (self.TYPE_GEOM + "?crs=epsg:2154", "COMP", "memory")
        
        # Eventuellement si vous voulez ajouter des attributs
        pr = self.layerOSM.dataProvider()
        pr.addAttributes([QgsField("position", QVariant.String)])
        self.layerOSM.commitChanges()
        
        # Style 
        props = {'color': '150,150,210,1', 'size':'1', 'color_border' : '0,0,0'}
        s = QgsFillSymbolV2.createSimple(props)
        self.layerOSM.setRendererV2(QgsSingleSymbolRendererV2(s))
        
        # Etiquette
        labelAdresse = QgsPalLayerSettings()
        labelAdresse.readFromLayer(self.layerOSM)
        labelAdresse.enabled = True 
        labelAdresse.textColor = QColor(0,0,0)

        # On initialise un champ
        labelAdresse.fieldName = 'position'

        # Correspond à l'emplacement autour du point           
        labelAdresse.placement = QgsPalLayerSettings.AroundPoint
        labelAdresse.setDataDefinedProperty(QgsPalLayerSettings.Size, True, True, '8', '')
        labelAdresse.dist = 1.5
    
        # On enregistre la couche
        labelAdresse.writeToLayer(self.layerOSM) 
                
        QgsMapLayerRegistry.instance().addMapLayer(self.layerOSM)
        
        
    
    def afficheContexte(self, currId):
        
        candList = []
        with open(self.uriGrille, 'r') as file:
            entete = True
            for line in file:
                if entete:
                    entete = False
                else:
                    # split
                    tab = line.split(";")
                    idref = tab[0]
                    
                    if currId == idref:
                        cand = dict()
                        cand['num'] = tab[2]    # 'num'
                        cand['id'] = tab[3]     # 'id'
                        cand['nom'] = tab[4]    # 'nom'
                        
                        n = len(self.NOM_DISTANCES)
                        
                        cand['pign1'] = tab[5 + 0 + n]
                        cand['pign2'] = tab[5 + 1 + n]
                        cand['decision'] = tab[5 + 2 + n]
                        
                        for i in range(n):
                            cand[self.NOM_DISTANCES[i]] = tab[5 + i]
                        
                        cand['geomref'] = tab[5 + 3 + n]
                        cand['geomcomp'] = tab[5 + 3 + n + 1]
                        
                        candList.append(cand)
                
            file.close()
            
        # print (len(candList))
        if len(candList) > 0:
                
            candidat = candList[1]
            
            self.removeFeatures()
            
            # ======================================================================================
            # Layer IGN
            pr = self.layerIGN.dataProvider()
            self.layerIGN.startEditing()
                
            poly = QgsFeature()
            poly.setGeometry(QgsGeometry.fromWkt(candidat['geomref']))
            pr.addFeatures([poly]) 
                
            # Sauvegarde les changements
            self.layerIGN.commitChanges()
        
            # ======================================================================================
            # Layer OSM
            pr = self.layerOSM.dataProvider()
            self.layerOSM.startEditing()
                
            for i in range(len(candList)):
                if i > 0:
                    poly = QgsFeature()
                    candidat = candList[i]
                    poly.setGeometry(QgsGeometry.fromWkt(candidat['geomcomp']))
                    poly.setAttributes([candidat['id']])
                    pr.addFeatures([poly]) 
                
                
            # Sauvegarde les changements
            self.layerOSM.commitChanges()
            
            # Zoom
            self.zoom()
            
        # remplir le tableau
        self.initTable(candList)
            
        
    def zoom(self):
        # ZOOM
        extent = self.layerOSM.extent()
        self.iface.mapCanvas().setExtent(extent)
        self.iface.mapCanvas().refresh()
        
        
    def doPrecedent(self):
        
        # On recupere l'id en cours
        currId = self.dockwidget.currentId.text()
        id = currId
        
        with open(self.uriGrille, 'r') as file:
            entete = True
            # cpt = 0
            for line in file:
                if entete:
                    # txtEntete = line
                    entete = False
                    # print (txtEntete)
                else:
                    # split
                    tab = line.split(";")
                    idref = tab[0]
                    
                    if currId == "-1":
                        id = idref
                        break
                        
                    else: 
                        if currId == idref:
                            id = str(int(id) - 1)
                            break
                
            file.close()
            
            
        self.dockwidget.currentId.setText(id)
        self.afficheContexte(id)
        
        
    def doSuivant(self):
        
        # On recupere l'id en cours
        currId = self.dockwidget.currentId.text()
        id = currId
        
        with open(self.uriGrille, 'r') as file:
            entete = True
            for line in file:
                if entete:
                    entete = False
                else:
                    # split
                    tab = line.split(";")
                    idref = tab[0]
                    
                    if currId == "-1":
                        id = idref
                        break
                        
                    else: 
                        if currId == idref:
                            id = str(int(id) + 1)
                            break
                
            file.close()
            
            
        self.dockwidget.currentId.setText(id)
        self.afficheContexte(id)
                
              
    def removeFeatures(self):
        self.layerOSM.startEditing()
    
        for feature in self.layerOSM.getFeatures():
            self.layerOSM.deleteFeature(feature.id())
        
        # commit to stop editing the layer
        self.layerOSM.commitChanges()
        
        
        self.layerIGN.startEditing()
    
        for feature in self.layerIGN.getFeatures():
            self.layerIGN.deleteFeature(feature.id())
        
        # commit to stop editing the layer
        self.layerIGN.commitChanges()
    
    
    def initTable(self, candList):

        self.vide(self.dockwidget.tableCoordFeu)
        
        if (len(candList)) == 0:
            self.dockwidget.tableCoordFeu.setRowCount(0)
            self.dockwidget.tableCoordFeu.setColumnCount(0)
        
        else:
            
            orange = QColor(255,196,109)
            vert = QColor(0,255,0)
            
            nbApp = 0
            nbNonApp = 0
            nbIndecis = 0
            labelRes = ''
            pign1 = ''
            pign2 = ''
            for i in range(len(candList)):
                
                candidat = candList[i]
                
                # On ajoute les coordonnées au tableau
                n = self.dockwidget.tableCoordFeu.rowCount()
                self.dockwidget.tableCoordFeu.insertRow(n);
        
                item1 = QTableWidgetItem(str(candidat['id']))
                self.dockwidget.tableCoordFeu.setItem(n, 0, item1)
                
                
                for i in range (len(self.NOM_DISTANCES)):
                    
                    nom = self.NOM_DISTANCES[i]
                    itemDistance = QTableWidgetItem(str(candidat[nom]))    
                    self.dockwidget.tableCoordFeu.setItem(n, 1 + i, itemDistance)
                    
                    s = float(candidat[nom])
                    
                    if i == 0:
                        seuil1 = float(self.dockwidget.D1_T1.text())
                        seuil2 = float(self.dockwidget.D1_T2.text())
                    if i == 1:
                        seuil1 = float(self.dockwidget.D2_T1.text())
                        seuil2 = float(self.dockwidget.D2_T2.text())
                    if i == 2:
                        seuil1 = float(self.dockwidget.D3_T1.text())
                        seuil2 = float(self.dockwidget.D3_T2.text())
                    if i == 3:
                        seuil1 = float(self.dockwidget.D4_T1.text())
                        seuil2 = float(self.dockwidget.D4_T2.text())
                    if i == 4:
                        seuil1 = float(self.dockwidget.D5_T1.text())
                        seuil2 = float(self.dockwidget.D5_T2.text())
                        
                    
                    if s < seuil1:
                        self.dockwidget.tableCoordFeu.item(n, 1 + i).setBackground(vert);
                    elif s < seuil2:
                        self.dockwidget.tableCoordFeu.item(n, 1 + i).setBackground(orange);
                    
                isNA = False
                if candidat['nom'] == 'NA':
                    isNA = True
                
                # print (candidat['decision'])
                
                # decision et resultat
                if (isNA and candidat['decision'] == 'true'):
                    nbNonApp = nbNonApp + 1
						
                if (not isNA and candidat['decision'] == 'true'):
                    nbApp = nbApp + 1
                    labelRes = candidat['id']
                    pign1 = candidat['pign1']
                    pign2 = candidat['pign2']
						
                if (isNA and candidat['decision'] == 'indécis'):
                    nbIndecis = nbIndecis + 1
						
                self.dockwidget.tableCoordFeu.scrollToBottom()
                
                if nbIndecis > 0:
                    self.dockwidget.labelResultat.setText('INDECIS')
                    self.dockwidget.labelResultat.setStyleSheet('color:black;font: 8pt MS Shell Dlg 2;background-color:orange')
                elif nbNonApp > 0:
                    self.dockwidget.labelResultat.setText("Pas d'appariement")
                    self.dockwidget.labelResultat.setStyleSheet('color:black;font: 8pt MS Shell Dlg 2;background-color:white')
                elif nbApp > 0:
                    self.dockwidget.labelResultat.setText("Appariement avec " + labelRes)
                    self.dockwidget.labelResultat.setStyleSheet('color:black;font: 8pt MS Shell Dlg 2;background-color:lightgreen')
                #else:
                #    print ('Inconnu')
            
                self.dockwidget.pign1.setText(pign1)
                self.dockwidget.pign2.setText(pign2)
                
        
        header = self.dockwidget.tableCoordFeu.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(3, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(4, QtGui.QHeaderView.ResizeToContents)
        
        
    
    
    def vide(self, table):

        self.dockwidget.tableCoordFeu.setRowCount(0)
        self.dockwidget.tableCoordFeu.setColumnCount(len(self.NOM_DISTANCES) + 1)
        
        colHearder = []
        colHearder.append('id')
        
        for i in range (len(self.NOM_DISTANCES)):
            nom = self.NOM_DISTANCES[i]
            nom = nom.replace('Distance', 'D').replace('distance','D')
            colHearder.append(nom)
            
            if i == 0:
                self.dockwidget.labelSeuil1.setText(nom)
            if i == 1:
                self.dockwidget.labelSeuil2.setText(nom)
            if i == 2:
                self.dockwidget.labelSeuil3.setText(nom)
            if i == 3:
                self.dockwidget.labelSeuil4.setText(nom)
            if i == 4:
                self.dockwidget.labelSeuil5.setText(nom)
        
        # 
        table.setHorizontalHeaderLabels(colHearder)
        
        