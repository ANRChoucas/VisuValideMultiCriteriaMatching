# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VisuValideMultiCriteriaMatching
                                 A QGIS plugin
 Visualisation et validation des résultats d'appariement multi-critères
                             -------------------
        begin                : 2018-07-09
        copyright            : (C) 2018 by IGN
        email                : mdvd@ign.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load VisuValideMultiCriteriaMatching class from file VisuValideMultiCriteriaMatching.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .visu_valide_MultiCriteriaMatching import VisuValideMultiCriteriaMatching
    return VisuValideMultiCriteriaMatching(iface)
