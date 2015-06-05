#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = u'Maxime DIVO'
__copyright__ = u'Copyright 2015, Maxime DIVO'
__credits__ = [u'Maxime DIVO']

__license__ = u'GPL v3'
__version__ = u'0.0.1'
__maintainer__ = u'Maxime DIVO'
__email__ = u'maxime.divo@gmail.com'
__status__ = u'Development'

import os.path as path

"""
Les icons
"""
URI = u'../share/ico'

def Uri(uri):
    return path.abspath(path.join(path.dirname( __file__ ), URI, uri))

APP = Uri(u'./lightning.ico')
    
FILE_32 = Uri(u'./32x32/document_empty.png')
OPEN_32 = Uri(u'./32x32/folder.png')
DISK_32 = Uri(u'./32x32/diskette.png')
DISKS_32 = Uri(u'./32x32/save_as.png')
PRINT_32 = Uri(u'./32x32/printer.png')

DEP_32 = Uri(u'./32x32/chart_organisation.png')
ADD_DEP_32 = Uri(u'./32x32/chart_organisation_add.png')
SUP_DEP_32 = Uri(u'./32x32/chart_organisation_delete.png')

ADD_32 = Uri(u'./32x32/add.png')
SUP_32 = Uri(u'./32x32/delete.png')

CUIVRE_16 = Uri(u'./16x16/coin_single_gold.png')
ALUMINIUM_16 = Uri(u'./16x16/coin_single_silver.png')
CUIVRE_32 = Uri(u'./32x32/coin_single_gold.png')
ALUMINIUM_32 = Uri(u'./32x32/coin_single_silver.png')

ZOOM_IN_32 = Uri(u'./32x32/zoom_in.png')
ZOOM_OUT_32 = Uri(u'./32x32/zoom_out.png')
ZOOM_FIT_32 = Uri(u'./32x32/zoom_fit.png')
ZOOM_REFR_32 = Uri(u'./32x32/zoom_refresh.png')
FULLSCREEN_32 = Uri(u'./32x32/view_fullscreen_view.png')
PANEL_32 = Uri(u'./32x32/panel.png')

OPEN_DB_32 = Uri(u'./32x32/folder_database.png')
EDIT_32 = Uri(u'./32x32/pencil_ruler.png')
