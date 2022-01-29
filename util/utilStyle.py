#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Fonctions pour le style

"""

from PyQt5.QtGui import QColor, QFont
from qgis.core import QgsFillSymbol, QgsSingleSymbolRenderer
from qgis.core import QgsTextFormat, QgsTextBufferSettings, QgsVectorLayerSimpleLabeling
from qgis.core import QgsPalLayerSettings
from qgis.core import QgsMarkerSymbol

def getRefPointStyle(layerREF):
    
    # Style 
    # On force une couleur bien précise
    symbol = QgsMarkerSymbol.createSimple({'name': 'square', 'color': 'red'})
    layerREF.renderer().setSymbol(symbol)
    # QColor.fromRgb(253,191,111)
    #props = {'color': '241,241,241,0', 'size':'1', 'color_border' : '255,0,0'}
    #s = QgsFillSymbol.createSimple(props)
    #layerREF.setRenderer(QgsSingleSymbolRenderer(s))
    
    # Etiquette
    layer_settings = QgsPalLayerSettings()
    # labelAdresse.readFromLayer(self.layerOSM)
    layer_settings.enabled = True 
    layer_settings.textColor = QColor(0,0,0)

    # On initialise un champ
    layer_settings.fieldName = """concat("nom", ' # ', "uri")"""
    layer_settings.isExpression = True

    # Correspond à l'emplacement autour du point           
    layer_settings.placement = QgsPalLayerSettings.AroundPoint
        
    # labelAdresse.setDataDefinedProperties(QgsPalLayerSettings.Size, True, True, '8')
    text_format = QgsTextFormat()
    text_format.setFont(QFont("Arial", 8))
    text_format.setSize(12)
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(1)
    buffer_settings.setColor(QColor("white"))
    text_format.setBuffer(buffer_settings)
        
    layer_settings.setFormat(text_format)
        
        
    layer_settings.dist = 1.5
    
    # On enregistre la couche
    # layer_settings.writeToLayer(self.layerCOMP) 
    layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
    layerREF.setLabelsEnabled(True)
    layerREF.setLabeling(layer_settings)
    
    return layerREF


def getCompPointStyle(layerCOMP, attr = 'id'):
    
    # Style 
    symbol = QgsMarkerSymbol.createSimple({'name': 'circle', 'color': '150,150,210,0', 'size':'2', 'color_border' : '0,0,0'})
    layerCOMP.renderer().setSymbol(symbol)
    
    # =========================================================    
    # Etiquette
    layer_settings = QgsPalLayerSettings()
    # labelAdresse.readFromLayer(self.layerOSM)
    layer_settings.enabled = True 
    layer_settings.textColor = QColor(0,0,0)

    # On initialise un champ
    if attr == 'nom':
        layer_settings.fieldName = """concat("nom", ' # ', "uri")"""
        layer_settings.isExpression = True
    else:
        layer_settings.fieldName = attr
    
    

    # Correspond à l'emplacement autour du point           
    layer_settings.placement = QgsPalLayerSettings.AroundPoint
        
    # labelAdresse.setDataDefinedProperties(QgsPalLayerSettings.Size, True, True, '8')
    text_format = QgsTextFormat()
    text_format.setFont(QFont("Arial", 8))
    text_format.setSize(12)
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(1)
    buffer_settings.setColor(QColor("white"))
    text_format.setBuffer(buffer_settings)
        
    layer_settings.setFormat(text_format)
        
        
    layer_settings.dist = 1.5
    
    # On enregistre la couche
    # layer_settings.writeToLayer(self.layerCOMP) 
    layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
    layerCOMP.setLabelsEnabled(True)
    layerCOMP.setLabeling(layer_settings)
    # self.layerOSM.triggerRepaint()
        
    return layerCOMP