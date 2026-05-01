import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance


#create maya window
def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QMainWindow)

def show():
    mw  = get_maya_main_window()
    win = QtWidgets.QDockWidget("Scatter Brush Tool", parent=mw)

    root = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(root)

    #status
    status_lbl = QtWidgets.QLabel("● Brush inactive")
    status_lbl.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(status_lbl)

    # paint and erase buttons side by side
    mode_row  = QtWidgets.QHBoxLayout()
    paint_btn = QtWidgets.QPushButton("Paint")
    erase_btn = QtWidgets.QPushButton("Erase")
    paint_btn.setCheckable(True)
    erase_btn.setCheckable(True)
    paint_btn.setChecked(True)
    mode_row.addWidget(paint_btn)
    mode_row.addWidget(erase_btn)
    layout.addLayout(mode_row)

    #activate
    activate_btn = QtWidgets.QPushButton("Activate Brush")
    activate_btn.setCheckable(True)
    layout.addWidget(activate_btn)

    #scroll 
    scroll    = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll_widget = QtWidgets.QWidget()
    scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
    scroll.setWidget(scroll_widget)
    layout.addWidget(scroll)

    #source objects
    src_group  = QtWidgets.QGroupBox("Source Objects")
    src_layout = QtWidgets.QVBoxLayout(src_group)

    source_list = QtWidgets.QListWidget()
    source_list.setSelectionMode(
        QtWidgets.QAbstractItemView.MultiSelection)
    source_list.setFixedHeight(90)
    src_layout.addWidget(source_list)

    hint = QtWidgets.QLabel("Select objects in viewport then click Add")
    src_layout.addWidget(hint)

    # add, refresh, remove buttons
    src_btn_row = QtWidgets.QHBoxLayout()
    add_btn     = QtWidgets.QPushButton("+ Add Sel")
    refresh_btn = QtWidgets.QPushButton("Refresh")
    remove_btn  = QtWidgets.QPushButton("Remove")
    src_btn_row.addWidget(add_btn)
    src_btn_row.addWidget(refresh_btn)
    src_btn_row.addWidget(remove_btn)
    src_layout.addLayout(src_btn_row)

    scroll_layout.addWidget(src_group)

    win.setWidget(root)
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, win)
    win.show()
    
    #brush settings
    brush_group  = QtWidgets.QGroupBox("Brush Settings")
    brush_layout = QtWidgets.QVBoxLayout(brush_group)
    radius_slider  = LabelledSlider("Radius",  1, 150, 30)
    density_slider = LabelledSlider("Density", 1,  20,  3)
    brush_layout.addWidget(radius_slider)
    brush_layout.addWidget(density_slider)
    scroll_layout.addWidget(brush_group)

show()

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