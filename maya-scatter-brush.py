import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance


#create maya window
def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QMainWindow)

def show()
    mw  = get_maya_main_window()
    win = QtWidgets.QDockWidget("Scatter Brush Tool", parent=mw)
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, win)
    win.show()
    

#create tool/pointer
#return

#ray cast setup
#viewport pointing
#creatre ray origin
#convert to cordinates
#create float pont

#loop for mesh

#return point 

#scatter instance
#no source -
#random selecton
#window error

#angle 0-360
#brush radius
#offset calculation
#vertical offest

#create object
#pick random, scale
#applying instance

#random rotation
#roate instance
#apply

#set instance position
#create scatter group
#group instances


#Drag/Brush
#call for brush

#call run brush

#run brush
#anchor point - drag

#call mesh and screen
# if nothing. stop

#if erase

#get list of library
#if empty
#
#loop with settings

#De/Activation
#activate
#create content
#press command
#drag command
#cursor to crosshair
#set undo mode to step

#deactivate reset
#delete events

#slider widgets
#slider width
#slider text
#slider in middle
#value change - update value
#return value

#Scatterbrush ui
#dockable pannel
#moveable pannel
#close
#float

#inactive/active label
#Create paint label
#create erase
#scroll 

#source objects
#brush settings
#randomness
#action/undo
#set mode
#activeate
#toggle brush
#add selection
#refresh obbjects
#remove event
#erase near
#clear all

#