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
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsProject, QgsVectorLayer
from qgis.core import QgsGeometry, QgsFeature
from qgis.core import QgsField



# Initialize Qt resources from file resources.py
from .resources import resources

# Import the code for the gui
from .gui.visu_resultat_dialog import VisuResultatDialog

from .util import utilFichier as util
from .util import utilStyle as style

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
            callback = self.initWidget,
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
        if self.layerCOMP != None:
            QgsProject.instance().removeMapLayers( [self.layerCOMP.id()] )
            
        if self.layerREF != None:
            QgsProject.instance().removeMapLayers( [self.layerREF.id()] )


    
    def initWidget(self):
        """Run method that performs all the real work"""
        
        if not self.pluginIsActive:
            
            self.pluginIsActive = True       
       
            if self.dockwidget == None:
                
                self.dockwidget = VisuResultatDialog()
                
                self.layerCOMP = None
                self.layerREF = None
                
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
                
                self.dockwidget.rbID.toggled.connect(self.visuDistance)
                self.dockwidget.rbD1.toggled.connect(self.visuDistance)
                self.dockwidget.rbD2.toggled.connect(self.visuDistance)
                self.dockwidget.rbD3.toggled.connect(self.visuDistance)
                self.dockwidget.rbD4.toggled.connect(self.visuDistance)
                self.dockwidget.rbD5.toggled.connect(self.visuDistance)
                

        self.iface.mapCanvas().refresh()
                
        # show the dockwidget
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        self.dockwidget.show()
        
    
    def importFichier(self):
        
        # On supprime les layers car on va les recreer
        self.vider()
        
        # On charge le chemin du fichier de résultat
        self.uriGrille = self.dockwidget.fileResultat.filePath().strip()
        # print (self.uriGrille)
        
        # On ouvre le fichier pour le type de la géométrie et les distances
        self.DISTANCE_NOM = []
        self.ATTRS_NOM = []
        self.CRITERE_SEUIL = []
        self.TYPE_GEOM = ''
        self.seuilIndecision = -1
        
        (DISTANCE_NOM, ATTRS_NOM, TYPE_GEOM, CRITERE_SEUIL, seuilIndecision) = util.entete(self.uriGrille)
        self.DISTANCE_NOM = DISTANCE_NOM
        self.ATTRS_NOM = ATTRS_NOM
        self.TYPE_GEOM = TYPE_GEOM
        self.CRITERE_SEUIL = CRITERE_SEUIL
        self.seuilIndecision = seuilIndecision
        
        
        self.dockwidget.seuilP.setText(str(self.seuilIndecision))
        # self.dockwidget.seuilP.setEnabled(False)
        
        #self.dockwidget.pign1.setEnabled(False)
        #self.dockwidget.pign2.setEnabled(False)
        
        self.dockwidget.currentId.setText("-1")
        
        self.createLayerComp()
        self.createLayerRef()
        
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
        
        # print (self.DISTANCE_NOM)
        # print (self.CRITERE_SEUIL)
        
        self.dockwidget.rbD1.setEnabled(False)
        self.dockwidget.rbD2.setEnabled(False)
        self.dockwidget.rbD3.setEnabled(False)
        self.dockwidget.rbD4.setEnabled(False)
        self.dockwidget.rbD5.setEnabled(False)
        
        
        for i in range (len(self.DISTANCE_NOM)):
            if i == 0:
                self.dockwidget.labelSeuil1.setEnabled(True)
                self.dockwidget.D1_T1.setEnabled(True)
                self.dockwidget.D1_T2.setEnabled(True)
                
                seuils = self.CRITERE_SEUIL[i]
                if len(seuils) > 0:
                    self.dockwidget.D1_T1.setText(seuils[0])
                if len(seuils) > 1:
                    self.dockwidget.D1_T2.setText(seuils[1])
                else:
                    self.dockwidget.D1_T2.setEnabled(False)
                
                self.dockwidget.rbD1.setEnabled(True)
            
            if i == 1:
                self.dockwidget.labelSeuil2.setEnabled(True)
                self.dockwidget.D2_T1.setEnabled(True)
                self.dockwidget.D2_T2.setEnabled(True)
                
                seuils = self.CRITERE_SEUIL[i]
                if len(seuils) > 0:
                    self.dockwidget.D2_T1.setText(seuils[0])
                if len(seuils) > 1:
                    self.dockwidget.D2_T2.setText(seuils[1])
                else:
                    self.dockwidget.D2_T2.setEnabled(False)
                    
                self.dockwidget.rbD2.setEnabled(True)
                    
            if i == 2:
                self.dockwidget.labelSeuil3.setEnabled(True)
                self.dockwidget.D3_T1.setEnabled(True)
                self.dockwidget.D3_T2.setEnabled(True)
                
                seuils = self.CRITERE_SEUIL[i]
                if len(seuils) > 0:
                    self.dockwidget.D3_T1.setText(seuils[0])
                if len(seuils) > 1:
                    self.dockwidget.D3_T2.setText(seuils[1])
                else:
                    self.dockwidget.D3_T2.setEnabled(False)
                    
                self.dockwidget.rbD3.setEnabled(True)
                    
            if i == 3:
                self.dockwidget.labelSeuil4.setEnabled(True)
                self.dockwidget.D4_T1.setEnabled(True)
                self.dockwidget.D4_T2.setEnabled(True)
                
                seuils = self.CRITERE_SEUIL[i]
                if len(seuils) > 0:
                    self.dockwidget.D4_T1.setText(seuils[0])
                if len(seuils) > 1:
                    self.dockwidget.D4_T2.setText(seuils[1])
                else:
                    self.dockwidget.D4_T2.setEnabled(False)
                    
                self.dockwidget.rbD4.setEnabled(True)
                    
            if i == 4:
                self.dockwidget.labelSeuil5.setEnabled(True)
                self.dockwidget.D5_T1.setEnabled(True)
                self.dockwidget.D5_T2.setEnabled(True)
                
                seuils = self.CRITERE_SEUIL[i]
                if len(seuils) > 0:
                    self.dockwidget.D5_T1.setText(seuils[0])
                if len(seuils) > 1:
                    self.dockwidget.D5_T2.setText(seuils[1])
                else:
                    self.dockwidget.D5_T2.setEnabled(False)
                    
                self.dockwidget.rbD5.setEnabled(True)
        
        
       

    def createLayerRef(self):
        # ======================================================================================
        # Layer IGN
        self.layerREF = QgsVectorLayer (self.TYPE_GEOM + "?crs=epsg:2154", "REF", "memory")
        
        if self.TYPE_GEOM == 'Polygon' or self.TYPE_GEOM == 'MultiPolygon':
            self.layerREF = style.getRefPolygoneStyle(self.layerREF)
            
        if self.TYPE_GEOM == 'Point' or self.TYPE_GEOM == 'MultiPoint':
            self.layerREF = style.getRefPointStyle(self.layerREF)
            
        QgsProject.instance().addMapLayer(self.layerREF)
            
            
        

    def createLayerComp(self):

        # ======================================================================================
        # Layer OSM
        self.layerCOMP = QgsVectorLayer (self.TYPE_GEOM + "?crs=epsg:2154", "COMP", "memory")
        
        # Eventuellement si vous voulez ajouter des attributs
        pr = self.layerCOMP.dataProvider()
        pr.addAttributes([QgsField("position", QVariant.String)])
        
        for i in range (len(self.ATTRS_NOM)):
            pr.addAttributes([QgsField(self.ATTRS_NOM[i], QVariant.String)])
        
        for i in range (len(self.DISTANCE_NOM)):
            if i == 0:
                pr.addAttributes([QgsField(self.DISTANCE_NOM[i], QVariant.Double)])
            if i == 1:
                pr.addAttributes([QgsField(self.DISTANCE_NOM[i], QVariant.Double)])
            if i == 2:
                pr.addAttributes([QgsField(self.DISTANCE_NOM[i], QVariant.Double)])
            if i == 3:
                pr.addAttributes([QgsField(self.DISTANCE_NOM[i], QVariant.Double)])
            if i == 4:
                pr.addAttributes([QgsField(self.DISTANCE_NOM[i], QVariant.Double)])
        
        self.layerCOMP.commitChanges()
        
        if self.TYPE_GEOM == 'Polygon' or self.TYPE_GEOM == 'MultiPolygon':
            self.layerCOMP = style.getCompPolygoneStyle(self.layerCOMP, 'position')
            
        if self.TYPE_GEOM == 'Point' or self.TYPE_GEOM == 'MultiPoint':
            self.layerCOMP = style.getCompPointStyle(self.layerCOMP)
                
        QgsProject.instance().addMapLayer(self.layerCOMP)
        
        
        
    
    def afficheContexte(self, currId):
        
        self.removeFeatures()
        
        candList = util.getCandidat(self.uriGrille, currId, self.DISTANCE_NOM, self.ATTRS_NOM)
        
        # print (len(candList))
        if len(candList) > 0:
                
            candidat = candList[1]
            
            # ======================================================================================
            # Layer REF
            pr = self.layerREF.dataProvider()
            self.layerREF.startEditing()
                
            poly = QgsFeature()
            poly.setGeometry(QgsGeometry.fromWkt(candidat['geomref']))
            pr.addFeatures([poly]) 
                
            # Sauvegarde les changements
            self.layerREF.commitChanges()
        
            # ======================================================================================
            # Layer OSM
            pr = self.layerCOMP.dataProvider()
            self.layerCOMP.startEditing()
                
            for i in range(len(candList)):
                if i > 0:
                    poly = QgsFeature()
                    candidat = candList[i]
                    poly.setGeometry(QgsGeometry.fromWkt(candidat['geomcomp']))
                    
                    attrs = []
                    attrs.append(str(candidat['id']))
                    
                    for j in range(len(self.ATTRS_NOM)):
                        nom = self.ATTRS_NOM[j]
                        attrs.append(candidat[nom])
                        
                    for i in range (len(self.DISTANCE_NOM)):
                        nom = self.DISTANCE_NOM[i]
                        s = float(candidat[nom])
                        #print (s)
                        attrs.append(s)

                    poly.setAttributes(attrs)
                    pr.addFeatures([poly]) 
                
            # Sauvegarde les changements
            self.layerCOMP.commitChanges()
            
            # Zoom
            self.zoom()
            
        # remplir le tableau
        self.initTable(candList)
            
        
    def zoom(self):
        # ZOOM
        extent = self.layerCOMP.extent()
        self.iface.mapCanvas().setExtent(extent)
        self.iface.mapCanvas().refresh()
        
        
    def doPrecedent(self):
        
        # On recupere l'id en cours
        currId = self.dockwidget.currentId.text()
        id = util.getLignePrec(self.uriGrille, currId)
        
        self.dockwidget.currentId.setText(str(id))
        self.afficheContexte(id)
        
        
    def doSuivant(self):
        
        # On recupere l'id en cours
        currId = self.dockwidget.currentId.text()
        id = util.getLigneSuiv(self.uriGrille, currId)
        
        self.dockwidget.currentId.setText(str(id))
        self.afficheContexte(id)
               
              
    def removeFeatures(self):
        self.layerREF.startEditing()
    
        for feature in self.layerREF.getFeatures():
            self.layerREF.deleteFeature(feature.id())
        
        # commit to stop editing the layer
        self.layerREF.commitChanges()
        
        # ===========================================
        
        self.layerCOMP.startEditing()
    
        for feature in self.layerCOMP.getFeatures():
            self.layerCOMP.deleteFeature(feature.id())
        
        # commit to stop editing the layer
        self.layerCOMP.commitChanges()
    
    
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
                
                for i in range(len(self.ATTRS_NOM)):
                    nom = self.ATTRS_NOM[i]
                    itemDistance = QTableWidgetItem(str(candidat[nom]))    
                    self.dockwidget.tableCoordFeu.setItem(n, 1 + i, itemDistance)
                
                
                for i in range (len(self.DISTANCE_NOM)):
                    
                    nom = self.DISTANCE_NOM[i]
                    itemDistance = QTableWidgetItem(str(candidat[nom]))    
                    self.dockwidget.tableCoordFeu.setItem(n, 1 + len(self.ATTRS_NOM) + i, itemDistance)
                    
                    s = float(candidat[nom])
                    
                    if i == 0:
                        if self.dockwidget.D1_T1.isEnabled():
                            seuil1 = float(self.dockwidget.D1_T1.text())
                        if self.dockwidget.D1_T2.isEnabled():
                            seuil2 = float(self.dockwidget.D1_T2.text())
                    if i == 1:
                        if self.dockwidget.D2_T1.isEnabled():
                            seuil1 = float(self.dockwidget.D2_T1.text())
                        if self.dockwidget.D2_T2.isEnabled():
                            seuil2 = float(self.dockwidget.D2_T2.text())
                    if i == 2:
                        if self.dockwidget.D3_T1.isEnabled():
                            seuil1 = float(self.dockwidget.D3_T1.text())
                        if self.dockwidget.D3_T2.isEnabled():
                            seuil2 = float(self.dockwidget.D3_T2.text())
                    if i == 3:
                        if self.dockwidget.D4_T1.isEnabled():
                            seuil1 = float(self.dockwidget.D4_T1.text())
                        if self.dockwidget.D4_T2.isEnabled():
                            seuil2 = float(self.dockwidget.D4_T2.text())
                    if i == 4:
                        if self.dockwidget.D5_T1.isEnabled():
                            seuil1 = float(self.dockwidget.D5_T1.text())
                        if self.dockwidget.D5_T2.isEnabled():
                            seuil2 = float(self.dockwidget.D5_T2.text())
                        
                        
                    # print (i)
                    if s < seuil1 and i < 2:
                        self.dockwidget.tableCoordFeu.item(n, 1 + i + len(self.ATTRS_NOM)).setBackground(vert);
                    elif s < seuil2 and i < 2:
                        self.dockwidget.tableCoordFeu.item(n, 1 + i + len(self.ATTRS_NOM)).setBackground(orange);
                    
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
                
        
#        header = self.dockwidget.tableCoordFeu.horizontalHeader()
#        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
#        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
#        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
#        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
#        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        
        
    
    
    def vide(self, table):

        self.dockwidget.tableCoordFeu.setRowCount(0)
        self.dockwidget.tableCoordFeu.setColumnCount(len(self.ATTRS_NOM) + len(self.DISTANCE_NOM) + 1)
        
        colHearder = []
        colHearder.append('id')
        
        for i in range (len(self.ATTRS_NOM)):
            nom = self.ATTRS_NOM[i]
            colHearder.append(nom)
        
        for i in range (len(self.DISTANCE_NOM)):
            nom = self.DISTANCE_NOM[i]
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
        
        
    
    def visuDistance(self):
        # print (self.DISTANCE_NOM[0])
        
        nomAttr = ''
#        if self.dockwidget.rbID.isChecked():
#            nomAttr = 'position'
#        
#        for i in range (len(self.DISTANCE_NOM)):
#            
#            if i == 0:
#                if self.dockwidget.rbD1.isChecked():
#                    nomAttr = self.DISTANCE_NOM[i]
#                    
#            if i == 1:
#                if self.dockwidget.rbD2.isChecked():
#                    nomAttr = self.DISTANCE_NOM[i]
#                    
#            if i == 2:
#                if self.dockwidget.rbD3.isChecked():
#                    nomAttr = self.DISTANCE_NOM[i]
#                    
#            if i == 3:
#                if self.dockwidget.rbD4.isChecked():
#                    nomAttr = self.DISTANCE_NOM[i]
#                    
#            if i == 4:
#                if self.dockwidget.rbD5.isChecked():
#                    nomAttr = self.DISTANCE_NOM[i]
#                    
#        # print (nomAttr)
#            
#        
#        if self.TYPE_GEOM == 'Point' or self.TYPE_GEOM == 'MultiPoint':
#            self.layerCOMP = style.getCompPointStyle(self.layerCOMP)
#        if self.TYPE_GEOM == 'Polygon' or self.TYPE_GEOM == 'MultiPolygon':
#            self.layerCOMP = style.getCompPolygoneStyle(self.layerCOMP, nomAttr)
#                
#        #self.iface.mapCanvas().refresh()
#        
#        self.layerCOMP.triggerRepaint()
#        self.iface.layerTreeView().refreshLayerSymbology(self.layerCOMP.id())
#        