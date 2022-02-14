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

from qgis.core import QgsProject, QgsVectorLayer, QgsVectorFileWriter
from qgis.core import QgsCoordinateReferenceSystem
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
        
        # On vide les champs de la fenêtre graphique
        self.dockwidget.fileResultat.setFilePath(None)
        self.dockwidget.fieldNbValidation.setText('0')
        self.dockwidget.fieldNbValidationProbleme.setText('0')
        self.vide(self.dockwidget.tableCoordFeu)
        self.dockwidget.D1_T1.setText("0")
        self.dockwidget.D1_T2.setText("0")
        self.dockwidget.D2_T1.setText("0")
        self.dockwidget.D3_T1.setText("0")
        self.dockwidget.seuilP.setText("0")
        self.dockwidget.pign1.setText("0")
        self.dockwidget.pign2.setText("0")
        self.dockwidget.labelResultat.setText('')
        self.dockwidget.labelResultat.setStyleSheet('color:black;font: 8pt MS Shell Dlg 2;background-color:white')
        self.dockwidget.fieldREFNom.setText("")
        self.dockwidget.fieldREFUri.setText("")
        self.dockwidget.fieldNbValidation.setText('0')
        self.dockwidget.fieldNbValidationProbleme.setText('0')
        self.dockwidget.fieldNbErreur.setText("0")
        self.dockwidget.fieldNbTODO.setText("0")
        self.dockwidget.rbTODO.setChecked(True)

        # On supprime les layers de la fenêtre        
        self.vider()

        # On ferme
        self.dockwidget.close()
        
    
    def vider(self):
        
        # ----------------------------------------------------------------------------
        # supprime les layers
        if self.layerCOMP != None:
            QgsProject.instance().removeMapLayers( [self.layerCOMP.id()] )
            self.layerCOMP = None
            
        if self.layerREF != None:
            QgsProject.instance().removeMapLayers( [self.layerREF.id()] )
            self.layerREF = None

        if self.layerLINK != None:
            QgsProject.instance().removeMapLayers( [self.layerLINK.id()] )
            self.layerLINK = None
            
    
    def initWidget(self):
        """Run method that performs all the real work"""
        
        if not self.pluginIsActive:
            
            self.pluginIsActive = True       
       
            if self.dockwidget == None:
                
                self.dockwidget = VisuResultatDialog()
                
                self.layerCOMP = None
                self.layerREF = None
                self.layerLINK = None
                
                self.dockwidget.btPrec.setStyleSheet('color : black;font: 8pt MS Shell Dlg 2')
                self.dockwidget.btSuiv.setStyleSheet('color : black;font: 8pt MS Shell Dlg 2')
                self.dockwidget.currentId.setStyleSheet('color : black;font: 8pt MS Shell Dlg 2')
                self.dockwidget.fileResultat.setStyleSheet('color : black;font: 8pt MS Shell Dlg 2')
                
                self.dockwidget.btSuiv.clicked.connect(self.doSuivant)
                self.dockwidget.btPrec.clicked.connect(self.doPrecedent)
                #self.dockwidget.currentId.setDisabled(True)
                self.dockwidget.currentId.setText("-1")
                
                self.dockwidget.btFermer.clicked.connect(self.onClosePlugin)
                self.dockwidget.btZoomGrille.clicked.connect(self.zoom)
                
                self.dockwidget.fileResultat.fileChanged.connect(self.importFichier)
                
                self.dockwidget.rbVALIDE.clicked.connect(self.valide)
                self.dockwidget.rbERREUR.clicked.connect(self.erreur)
                self.dockwidget.rbINDECIS.clicked.connect(self.indecis)
                self.dockwidget.rbTODO.clicked.connect(self.todo)
                
                self.dockwidget.btID.clicked.connect(self.affid)
                self.dockwidget.btNom.clicked.connect(self.affnom)
                
                self.dockwidget.rbTODO.setEnabled(True)
                self.dockwidget.rbVALIDE.setEnabled(False)
                self.dockwidget.rbERREUR.setEnabled(False)
                self.dockwidget.rbINDECIS.setEnabled(False)
                
                self.dockwidget.btSauvegarderFermer.clicked.connect(self.saveclose)
                self.dockwidget.btSauvegarderFermer.setEnabled(False)
                
                self.dockwidget.fieldREFNom.setText("")
                self.dockwidget.fieldREFUri.setText("")
                
                self.dockwidget.btNextApp.clicked.connect(self.doSuivantAppariement)
                self.dockwidget.btNextValid.clicked.connect(self.doSuivantValide)
                self.dockwidget.btNextTodo.clicked.connect(self.doSuivantTodo)
                self.dockwidget.btNextDifficile.clicked.connect(self.doSuivantDifficile)
                self.dockwidget.btNextErreur.clicked.connect(self.doSuivantErreur)
                

        self.iface.mapCanvas().refresh()
                
        # show the dockwidget
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        self.dockwidget.show()
        
    
    def saveclose(self):
        
        if self.featLINK != None:
            print (self.uriFileLink)
            self.layerLINK.setSubsetString("")
            # Save memory layer to file
            crs = QgsCoordinateReferenceSystem("epsg:2154")
            error = QgsVectorFileWriter.writeAsVectorFormat(self.layerLINK, self.uriFileLink, "UTF-8", crs , "ESRI Shapefile")
        
            # On empeche l'enregistrement
            self.dockwidget.btSauvegarderFermer.setEnabled(False)

            if error == QgsVectorFileWriter.NoError:
                print ("success! writing new memory layer")

        # On ferme
        self.onClosePlugin()
        
    # 1
    # self.NB_VALIDE
    # 2    
    # self.NB_PROBLEME
    # 0
    # self.NB_ERREUR
    # -1
    # self.NB_TODO
    # self.majNombreValidation()
    
    def updateNB(self, oldval, newval):
        if oldval == 1:
            self.NB_VALIDE -= 1
        if oldval == 2:
            self.NB_PROBLEME -= 1
        if oldval == 0:
            self.NB_ERREUR -= 1
        if oldval == -1:
            self.NB_TODO -= 1
            
        if newval == 1:
            self.NB_VALIDE += 1
        if newval == 2:
            self.NB_PROBLEME += 1
        if newval == 0:
            self.NB_ERREUR += 1
        if newval == -1:
            self.NB_TODO += 1
        
    def valide(self):
        if self.featLINK != None:
            # On récupère le code
            validation = self.featLINK.attributes()[2]
            self.updateNB(validation, 1)
            self.majNombreValidation()
            
            self.layerLINK.setSubsetString("")
            self.layerLINK.startEditing()
            self.prlink = self.layerLINK.dataProvider()
            self.layerLINK.changeAttributeValue(self.featLINK.id(), 2, 1)
            self.layerLINK.commitChanges()
            self.layerLINK.setSubsetString(" ID_REF = '" + str(self.idFeatLINK) + "'")
            for feat in self.layerLINK.getFeatures():
                self.featLINK = feat

    def erreur(self):
        if self.featLINK != None:
            # On récupère le code
            validation = self.featLINK.attributes()[2]
            self.updateNB(validation, 0)
            self.majNombreValidation()
            
            self.layerLINK.setSubsetString("")
            self.layerLINK.startEditing()
            self.prlink = self.layerLINK.dataProvider()
            self.layerLINK.changeAttributeValue(self.featLINK.id(), 2, 0)
            self.layerLINK.commitChanges()
            self.layerLINK.setSubsetString(" ID_REF = '" + str(self.idFeatLINK) + "'")
            for feat in self.layerLINK.getFeatures():
                self.featLINK = feat
            
    def indecis(self):
        if self.featLINK != None:
            # On récupère le code
            validation = self.featLINK.attributes()[2]
            self.updateNB(validation, 2)
            self.majNombreValidation()
            
            self.layerLINK.setSubsetString("")
            self.layerLINK.startEditing()
            self.prlink = self.layerLINK.dataProvider()
            self.layerLINK.changeAttributeValue(self.featLINK.id(), 2, 2)
            self.layerLINK.commitChanges()
            self.layerLINK.setSubsetString(" ID_REF = '" + str(self.idFeatLINK) + "'")
            for feat in self.layerLINK.getFeatures():
                self.featLINK = feat
            
    def todo(self):
        if self.featLINK != None:
            # On récupère le code
            validation = self.featLINK.attributes()[2]
            self.updateNB(validation, -1)
            self.majNombreValidation()
            
            self.layerLINK.setSubsetString("")
            self.layerLINK.startEditing()
            self.prlink = self.layerLINK.dataProvider()
            self.layerLINK.changeAttributeValue(self.featLINK.id(), 2, -1)
            self.layerLINK.commitChanges()
            self.layerLINK.setSubsetString(" ID_REF = '" + str(self.idFeatLINK) + "'")
            for feat in self.layerLINK.getFeatures():
                self.featLINK = feat
        
    
    def affid(self):
        self.layerCOMP = style.getCompPointStyle(self.layerCOMP, 'id')
    def affnom(self):
        self.layerCOMP = style.getCompPointStyle(self.layerCOMP, 'nom')
    
        
    
    def importFichier(self):
        
        # On charge le chemin du fichier de résultat
        self.uriGrille = self.dockwidget.fileResultat.filePath().strip()
        # print ('uri', self.uriGrille)
        
        if self.uriGrille != None and self.uriGrille.strip() != '':
            # On supprime les layers car on va les recreer
            self.vider()
            
            # On ouvre le fichier pour le type de la géométrie et les distances
            self.DISTANCE_NOM = []
            self.CRITERE_SEUIL = []
            self.TYPE_GEOM = ''
            self.seuilIndecision = -1
            
            (DISTANCE_NOM, TYPE_GEOM, CRITERE_SEUIL, seuilIndecision) = util.entete(self.uriGrille)
            self.DISTANCE_NOM = DISTANCE_NOM
            self.TYPE_GEOM = TYPE_GEOM
            self.CRITERE_SEUIL = CRITERE_SEUIL
            self.seuilIndecision = seuilIndecision
            
            self.dockwidget.seuilP.setText(str(self.seuilIndecision))
            
            self.dockwidget.seuilP.setEnabled(False)
            self.dockwidget.pign1.setEnabled(False)
            self.dockwidget.pign2.setEnabled(False)
            
            self.dockwidget.currentId.setText("-1")
            
            self.createLayerComp()
            self.createLayerRef()
            self.createLayerLink()
            
            self.dockwidget.labelSeuil1.setEnabled(False)
            self.dockwidget.labelSeuil2.setEnabled(False)
            self.dockwidget.labelSeuil3.setEnabled(False)
            
            self.dockwidget.D1_T1.setText(self.CRITERE_SEUIL[0][0])
            self.dockwidget.D1_T2.setText(self.CRITERE_SEUIL[0][1])
            self.dockwidget.D2_T1.setText(self.CRITERE_SEUIL[1][0])
            self.dockwidget.D3_T1.setText(self.CRITERE_SEUIL[2][0])
            
            #self.dockwidget.fieldNbValidation.setEnabled(False)
            #self.dockwidget.fieldNbValidationProbleme.setEnabled(False)
        
        
        

    def createLayerRef(self):
        # =====================================================================
        #  Layer REF
        self.layerREF = QgsVectorLayer ("Point?crs=epsg:2154", "REF", "memory")
        self.layerREF.startEditing()
        pr = self.layerREF.dataProvider()
        pr.addAttributes([QgsField("uri", QVariant.String)])
        pr.addAttributes([QgsField("nom", QVariant.String)])
        self.layerREF.commitChanges()
        
        self.layerREF = style.getRefPointStyle(self.layerREF)
        QgsProject.instance().addMapLayer(self.layerREF)


    def createLayerComp(self):
        # =====================================================================
        #  Layer COMP (candidat)
        self.layerCOMP = QgsVectorLayer ("Point?crs=epsg:2154", "COMP", "memory")
        self.layerCOMP.startEditing()
        pr = self.layerCOMP.dataProvider()
        pr.addAttributes([QgsField("position", QVariant.String)])
        pr.addAttributes([QgsField("id", QVariant.String)])
        pr.addAttributes([QgsField("uri", QVariant.String)])
        pr.addAttributes([QgsField("nom", QVariant.String)])
        
        pr.addAttributes([QgsField(self.DISTANCE_NOM[0], QVariant.Double)])
        pr.addAttributes([QgsField(self.DISTANCE_NOM[1], QVariant.Double)])
        pr.addAttributes([QgsField(self.DISTANCE_NOM[2], QVariant.Double)])
        self.layerCOMP.commitChanges()
        
        self.layerCOMP = style.getCompPointStyle(self.layerCOMP)
        QgsProject.instance().addMapLayer(self.layerCOMP)
        
        
    def createLayerLink(self):
        # =====================================================================
        # Layer liens d'appariement
        self.uriFileLink = self.uriGrille.split(".")[0] + "-APP.shp"
        if not os.path.isfile(self.uriFileLink):
            
            # Il faut activer la sauvegarde
            self.dockwidget.btSauvegarderFermer.setEnabled(True)
            
            # il faut le créer en memory pour commencer
            self.layerLINK = QgsVectorLayer ("LineString?crs=EPSG:2154", "Liens appariement", "memory")
            pr = self.layerLINK.dataProvider()
            pr.addAttributes([QgsField("ID_REF", QVariant.String),
                  QgsField("ID_COMP",  QVariant.String),
                  QgsField("VALIDATION", QVariant.Int)])
            self.layerLINK.updateFields() 

            LINKS = util.lienappariement(self.uriGrille, self.DISTANCE_NOM)
            for link in LINKS:
                # f.write(link[0] + ";" + link[1] + ";-1;" + ligne.asWkt() + "\n")
                p1 = QgsGeometry.fromWkt(link[2]).asPoint()
                p2 = QgsGeometry.fromWkt(link[3]).asPoint()
                ligne = QgsGeometry.fromPolylineXY([p1,p2])
                
                f = QgsFeature()
                f.setGeometry(ligne)
                f.setAttributes([link[0], link[1], -1.0])
                pr.addFeature(f)
            
            self.layerLINK.updateExtents() 
            self.dockwidget.fieldNbValidation.setText('0')
            self.dockwidget.fieldNbValidationProbleme.setText('0')
            self.dockwidget.fieldNbErreur.setText("0")
            self.dockwidget.fieldNbTODO.setText("0")
            
        else:
            # On charge le fichier CSV
            self.layerLINK = QgsVectorLayer (self.uriFileLink, "Liens appariement", "ogr")
        
        
        self.layerLINK.setSubsetString(" VALIDATION = 1 ")
        self.NB_VALIDE = self.layerLINK.featureCount()
        
        self.layerLINK.setSubsetString(" VALIDATION = 2")
        self.NB_PROBLEME = self.layerLINK.featureCount()
        
        self.layerLINK.setSubsetString(" VALIDATION = 0")
        self.NB_ERREUR = self.layerLINK.featureCount()
        
        self.layerLINK.setSubsetString(" VALIDATION = -1")
        self.NB_TODO = self.layerLINK.featureCount()
        
        self.majNombreValidation()
        
        self.layerLINK.setSubsetString("1 = 0")
        QgsProject.instance().addMapLayer(self.layerLINK)
        
        single_symbol_renderer = self.layerLINK.renderer()
        symbol = single_symbol_renderer.symbol()
        symbol.setColor(QColor.fromRgb(31, 120, 180))
        symbol.setWidth(0.6)


    def majNombreValidation(self):
        # =====================================================================
        self.dockwidget.fieldNbValidation.setText(str(self.NB_VALIDE))
        self.dockwidget.fieldNbValidationProbleme.setText(str(self.NB_PROBLEME))
        self.dockwidget.fieldNbErreur.setText(str(self.NB_ERREUR))
        self.dockwidget.fieldNbTODO.setText(str(self.NB_TODO))
    
    
    def afficheContexte(self, currId):
        # =====================================================================
        self.removeFeatures()
        #print (currId)
        d = util.getRefInfo(self.uriGrille, currId)
        if d!= None:
            self.dockwidget.fieldREFNom.setText(d[0])
            self.dockwidget.fieldREFUri.setText(d[1].replace('http://purl.org/choucas.ign.fr/oor#', ''))
        
        candList = util.getCandidat(self.uriGrille, currId, self.DISTANCE_NOM)
        if len(candList) > 0:
            candidat = candList[1]
            
            # =================================================================
            # Layer REF
            pr = self.layerREF.dataProvider()
            self.layerREF.startEditing()
            poly = QgsFeature()
            poly.setGeometry(QgsGeometry.fromWkt(candidat['geomref']))
            poly.setAttributes([candidat['uriref'].replace('http://purl.org/choucas.ign.fr/oor#', ''), candidat['nomref']])
            pr.addFeatures([poly]) 
            self.layerREF.commitChanges()
        
            # =================================================================
            # Layer OSM
            pr = self.layerCOMP.dataProvider()
            self.layerCOMP.startEditing()
            for i in range(len(candList)):
                if i > 0:
                    poly = QgsFeature()
                    candidat = candList[i]
                    poly.setGeometry(QgsGeometry.fromWkt(candidat['geomcomp']))
                    
                    attrs = []
                    attrs.append(str(candidat['num']))
                    attrs.append(str(candidat['id']))
                    attrs.append(str(candidat['uri'].replace('http://purl.org/choucas.ign.fr/oor#', '')))
                    attrs.append(str(candidat['nom']))
                    
                    for i in range (len(self.DISTANCE_NOM)):
                        nom = self.DISTANCE_NOM[i]
                        s = candidat[nom]
                        attrs.append(s)

                    poly.setAttributes(attrs)
                    pr.addFeatures([poly]) 
            # Sauvegarde les changements
            self.layerCOMP.commitChanges()
            
            # =================================================================
            # Layer LINK
            self.layerLINK.setSubsetString(" ID_REF = '" + candidat['idref'] + "'")
            
            # =================================================================
            # Zoom
            self.zoom()
            
        # =================================================================
        # remplir le tableau
        self.initTable(candList)
        
        # =================================================================
        # validation
        validation = -1
        #self.dockwidget.rbTODO.setChecked(False)
        cptLien = 0
        self.featLINK = None
        for feat in self.layerLINK.getFeatures():
            validation = feat.attributes()[2]
            cptLien += 1
            self.featLINK = feat
            self.idFeatLINK = feat.attributes()[0]
            
        if cptLien == 0:
            #self.dockwidget.btEdit.setEnabled(False)
            self.dockwidget.rbERREUR.setEnabled(False)
            self.dockwidget.rbVALIDE.setEnabled(False)
            self.dockwidget.rbINDECIS.setEnabled(False)
        else:
            #self.dockwidget.btEdit.setEnabled(True)
            self.dockwidget.rbERREUR.setEnabled(True)
            self.dockwidget.rbVALIDE.setEnabled(True)
            self.dockwidget.rbINDECIS.setEnabled(True)
            
        if validation == -1:
            self.dockwidget.rbTODO.setChecked(True)
        if validation == 0:
            self.dockwidget.rbERREUR.setChecked(True)
        if validation == 1:
            self.dockwidget.rbVALIDE.setChecked(True)
        if validation == 2:
            self.dockwidget.rbINDECIS.setChecked(True)
            
            
    def getLabelValidation(self, id):
        # validation
        validation = -1
        cptLien = 0
        
        self.layerLINK.setSubsetString(" ID_REF = '" + id + "'")
        for liens in self.layerLINK.getFeatures():
            attrs = liens.attributes()
            if attrs[0] == id:
                validation = attrs[2]
                cptLien += 1
        return validation
        
    
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
        #print (currId)
        id = util.getLigneSuiv(self.uriGrille, currId)
        #print ('id', id)
        
        self.dockwidget.currentId.setText(str(id))
        self.afficheContexte(id)
        
    
    def doSuivantValide(self):
        # On recupere l'id en cours
        currId = self.dockwidget.currentId.text()
        
        cpt = 0
        while cpt < 15000:
            id = util.getLigneSuiv(self.uriGrille, currId)
            if id == -1:
                break
        
            candList = util.getCandidat(self.uriGrille, id, self.DISTANCE_NOM)
            labels = util.getLabelResultat(candList)
            lab = labels[0]
            valid = self.getLabelValidation(id)
            if 'Appariement' == lab and valid == 1:
                break
                
            currId = id
            cpt += 1
        
        self.dockwidget.currentId.setText(str(id))
        self.afficheContexte(id)
        
    def doSuivantTodo(self):
        # On recupere l'id en cours
        currId = self.dockwidget.currentId.text()
        
        cpt = 0
        while cpt < 15000:
            id = util.getLigneSuiv(self.uriGrille, currId)
            if id == -1:
                break
        
            candList = util.getCandidat(self.uriGrille, id, self.DISTANCE_NOM)
            labels = util.getLabelResultat(candList)
            lab = labels[0]
            valid = self.getLabelValidation(id)
            if 'Appariement' == lab and valid == -1:
                break
                
            currId = id
            cpt += 1
        
        self.dockwidget.currentId.setText(str(id))
        self.afficheContexte(id)
        
        
    def doSuivantAppariement(self):
        # On recupere l'id en cours
        currId = self.dockwidget.currentId.text()
        
        cpt = 0
        while cpt < 15000:
            id = util.getLigneSuiv(self.uriGrille, currId)
            if id == -1:
                break
        
            candList = util.getCandidat(self.uriGrille, id, self.DISTANCE_NOM)
            labels = util.getLabelResultat(candList)
            lab = labels[0]
            if 'Appariement' == lab:
                break
                
            currId = id
            cpt += 1
        
        self.dockwidget.currentId.setText(str(id))
        self.afficheContexte(id)
        
        
    def doSuivantDifficile(self):
        # On recupere l'id en cours
        currId = self.dockwidget.currentId.text()
        
        cpt = 0
        while cpt < 15000:
            id = util.getLigneSuiv(self.uriGrille, currId)
            if id == -1:
                break
        
            candList = util.getCandidat(self.uriGrille, id, self.DISTANCE_NOM)
            labels = util.getLabelResultat(candList)
            lab = labels[0]
            valid = self.getLabelValidation(id)
            if 'Appariement' == lab and valid == 2:
                break
                
            currId = id
            cpt += 1
        
        self.dockwidget.currentId.setText(str(id))
        self.afficheContexte(id)
        
    
    def doSuivantErreur(self):
        # On recupere l'id en cours
        currId = self.dockwidget.currentId.text()
        
        cpt = 0
        while cpt < 15000:
            id = util.getLigneSuiv(self.uriGrille, currId)
            if id == -1:
                break
        
            candList = util.getCandidat(self.uriGrille, id, self.DISTANCE_NOM)
            labels = util.getLabelResultat(candList)
            lab = labels[0]
            valid = self.getLabelValidation(id)
            if 'Appariement' == lab and valid == 0:
                break
                
            currId = id
            cpt += 1
        
        self.dockwidget.currentId.setText(str(id))
        self.afficheContexte(id)
               
              
    def removeFeatures(self):
        # ===========================================
        self.layerREF.startEditing()
        for feature in self.layerREF.getFeatures():
            self.layerREF.deleteFeature(feature.id())
        self.layerREF.commitChanges()
        
        # ===========================================
        self.layerCOMP.startEditing()
        for feature in self.layerCOMP.getFeatures():
            self.layerCOMP.deleteFeature(feature.id())
        self.layerCOMP.commitChanges()
        
        # ===========================================
        self.layerLINK.setSubsetString("1=0")
        
    
    
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
                
                #self.dockwidget.tableCoordFeu.setItem(n, 1, QTableWidgetItem(str(candidat['nom'])))
                #uri = str(candidat['uri'].replace('http://purl.org/choucas.ign.fr/oor#', ''))
                #self.dockwidget.tableCoordFeu.setItem(n, 2, QTableWidgetItem(uri))
                
                for i in range (len(self.DISTANCE_NOM)):
                    nom = self.DISTANCE_NOM[i]
                    itemDistance = QTableWidgetItem(str(candidat[nom]))    
                    self.dockwidget.tableCoordFeu.setItem(n, 1 + i, itemDistance)
                    
                    s = float(candidat[nom])
                    seuil1 = 0
                    seuil2 = 0
                    if i == 0:
                        if self.dockwidget.D1_T1.isEnabled():
                            seuil1 = float(self.dockwidget.D1_T1.text())
                        if self.dockwidget.D1_T2.isEnabled():
                            seuil2 = float(self.dockwidget.D1_T2.text())
                    if i == 1:
                        if self.dockwidget.D2_T1.isEnabled():
                            seuil1 = float(self.dockwidget.D2_T1.text())
                    if i == 2:
                        if self.dockwidget.D3_T1.isEnabled():
                            seuil1 = float(self.dockwidget.D3_T1.text())
#                    # print (i)
                    if s < seuil1 and i < 2:
                        self.dockwidget.tableCoordFeu.item(n, 1 + i).setBackground(vert);
                    elif s < seuil2 and i < 2:
                        self.dockwidget.tableCoordFeu.item(n, 1 + i).setBackground(orange);
                    
                isNA = False
                if candidat['nom'] == 'NA':
                    isNA = True
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
        self.dockwidget.tableCoordFeu.setColumnCount(4)
        
        colHearder = []
        colHearder.append('id')
        #colHearder.append('nom')
        #colHearder.append('uri')
        
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
        # 
        table.setHorizontalHeaderLabels(colHearder)
        
        
    
