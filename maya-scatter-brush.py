import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.OpenMaya as om
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance

def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QMainWindow)

def get_mesh_hit(screen_x, screen_y):
    # get the active viewport and shoot a ray through the screen position
    view       = omui.M3dView.active3dView()
    ray_origin = om.MPoint()
    ray_dir    = om.MVector()
    view.viewToWorld(int(screen_x), int(screen_y), ray_origin, ray_dir)

    # convert to float versions for closestIntersection
    ray_o = om.MFloatPoint(ray_origin.x, ray_origin.y, ray_origin.z)
    ray_d = om.MFloatVector(ray_dir.x,   ray_dir.y,   ray_dir.z)

    closest_dist   = float("inf")
    closest_point  = None
    closest_normal = om.MVector(0, 1, 0)

    # loop through every mesh in the scene
    dag_iter = om.MItDag(om.MItDag.kDepthFirst, om.MFn.kMesh)
    while not dag_iter.isDone():
        dag_path = om.MDagPath()
        dag_iter.getPath(dag_path)
        try:
            mesh_fn = om.MFnMesh(dag_path)
            if mesh_fn.isIntermediateObject():
                dag_iter.next()
                continue

            hit_pt   = om.MFloatPoint()
            util     = om.MScriptUtil()
            util.createFromInt(0)
            face_ptr = util.asIntPtr()

            hit = mesh_fn.closestIntersection(
                ray_o, ray_d, None, None, False,
                om.MSpace.kWorld, 99999, False, None,
                hit_pt, None, face_ptr, None, None, None
            )

            if hit:
                dist = ray_o.distanceTo(hit_pt)
                if dist < closest_dist:
                    closest_dist  = dist
                    closest_point = om.MPoint(hit_pt.x, hit_pt.y, hit_pt.z)
                    face_idx = util.getInt(face_ptr)
                    norms    = om.MFloatVectorArray()
                    mesh_fn.getFaceVertexNormals(
                        face_idx, norms, om.MSpace.kWorld)
                    if norms.length() > 0:
                        n = norms[0]
                        closest_normal = om.MVector(n.x, n.y, n.z).normal()
        except Exception:
            pass
        dag_iter.next()

    return closest_point, closest_normal

SCATTER_GROUP = "scatter_grp"
DRAG_CTX      = "scatterBrushDraggerCtx"

_ui_ref = None

def _ctx_press():
    _run_brush()

def _ctx_drag():
    _run_brush()

def _run_brush():
    ui = _ui_ref
    if ui is None:
        return

    # get screen coordinates from the dragger context
    ax, ay = cmds.draggerContext(DRAG_CTX, q=True, anchorPoint=True)[:2]
    dx, dy = cmds.draggerContext(DRAG_CTX, q=True, dragPoint=True)[:2]
    sx = dx if dx != 0 else ax
    sy = dy if dy != 0 else ay

    # cast a ray and find the hit point
    hit_point, hit_normal = get_mesh_hit(sx, sy)
    if hit_point is None:
        print("no hit")
        return

    print("hit at", hit_point.x, hit_point.y, hit_point.z)

def activate_context():
    if cmds.draggerContext(DRAG_CTX, exists=True):
        cmds.deleteUI(DRAG_CTX)
    cmds.draggerContext(
        DRAG_CTX,
        pressCommand = "_ctx_press()",
        dragCommand  = "_ctx_drag()",
        cursor       = "crossHair",
        undoMode     = "step",
    )
    cmds.setToolTo(DRAG_CTX)

def deactivate_context():
    cmds.setToolTo("selectSuperContext")
    if cmds.draggerContext(DRAG_CTX, exists=True):
        cmds.deleteUI(DRAG_CTX)


class LabelledSlider(QtWidgets.QWidget):
    def __init__(self, label, lo, hi, default, parent=None):
        super().__init__(parent)
        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        lbl = QtWidgets.QLabel(label)
        lbl.setFixedWidth(90)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(lo)
        self.slider.setMaximum(hi)
        self.slider.setValue(default)
        self.readout = QtWidgets.QLabel(str(default))
        self.readout.setFixedWidth(35)
        self.readout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.slider.valueChanged.connect(lambda v: self.readout.setText(str(v)))
        row.addWidget(lbl)
        row.addWidget(self.slider)
        row.addWidget(self.readout)

    def value(self):
        return self.slider.value()


class ScatterBrushUI(QtWidgets.QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Scatter Brush Tool", parent)
        self.mode = "paint"
        self._build_ui()

    def _build_ui(self):
        root   = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(root)

        # status label
        self.status_lbl = QtWidgets.QLabel("● Brush inactive")
        self.status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status_lbl)

        # mode buttons
        mode_row       = QtWidgets.QHBoxLayout()
        self.paint_btn = QtWidgets.QPushButton("Paint")
        self.erase_btn = QtWidgets.QPushButton("Erase")
        self.paint_btn.setCheckable(True)
        self.erase_btn.setCheckable(True)
        self.paint_btn.setChecked(True)
        self.paint_btn.clicked.connect(lambda: self._set_mode("paint"))
        self.erase_btn.clicked.connect(lambda: self._set_mode("erase"))
        mode_row.addWidget(self.paint_btn)
        mode_row.addWidget(self.erase_btn)
        layout.addLayout(mode_row)

        # activate button
        self.activate_btn = QtWidgets.QPushButton("Activate Brush")
        self.activate_btn.setCheckable(True)
        self.activate_btn.toggled.connect(self._toggle_brush)
        layout.addWidget(self.activate_btn)

        # scroll area
        scroll        = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # source objects
        src_group  = QtWidgets.QGroupBox("Source Objects")
        src_layout = QtWidgets.QVBoxLayout(src_group)
        self.source_list = QtWidgets.QListWidget()
        self.source_list.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection)
        self.source_list.setFixedHeight(90)
        src_layout.addWidget(self.source_list)
        src_layout.addWidget(QtWidgets.QLabel("Select objects then click Add"))
        src_btn_row = QtWidgets.QHBoxLayout()
        add_btn     = QtWidgets.QPushButton("+ Add Sel")
        refresh_btn = QtWidgets.QPushButton("Refresh")
        remove_btn  = QtWidgets.QPushButton("Remove")
        add_btn.clicked.connect(self._add_sel)
        refresh_btn.clicked.connect(self._refresh)
        remove_btn.clicked.connect(self._remove_src)
        src_btn_row.addWidget(add_btn)
        src_btn_row.addWidget(refresh_btn)
        src_btn_row.addWidget(remove_btn)
        src_layout.addLayout(src_btn_row)
        scroll_layout.addWidget(src_group)

        # brush settings
        brush_group  = QtWidgets.QGroupBox("Brush Settings")
        brush_layout = QtWidgets.QVBoxLayout(brush_group)
        self.radius_slider  = LabelledSlider("Radius",  1, 150, 30)
        self.density_slider = LabelledSlider("Density", 1,  20,  3)
        brush_layout.addWidget(self.radius_slider)
        brush_layout.addWidget(self.density_slider)
        scroll_layout.addWidget(brush_group)

        # randomization
        rand_group  = QtWidgets.QGroupBox("Randomization")
        rand_layout = QtWidgets.QVBoxLayout(rand_group)
        self.scale_min_slider = LabelledSlider("Scale Min", 1, 50,  8)
        self.scale_max_slider = LabelledSlider("Scale Max", 1, 50, 15)
        self.offset_slider    = LabelledSlider("Offset",    0, 100, 20)
        rand_layout.addWidget(self.scale_min_slider)
        rand_layout.addWidget(self.scale_max_slider)
        rand_layout.addWidget(self.offset_slider)
        rand_layout.addWidget(QtWidgets.QLabel("Random Rotation Axes:"))
        rot_row       = QtWidgets.QHBoxLayout()
        self.rot_x_cb = QtWidgets.QCheckBox("X")
        self.rot_y_cb = QtWidgets.QCheckBox("Y")
        self.rot_z_cb = QtWidgets.QCheckBox("Z")
        self.rot_y_cb.setChecked(True)
        rot_row.addWidget(self.rot_x_cb)
        rot_row.addWidget(self.rot_y_cb)
        rot_row.addWidget(self.rot_z_cb)
        rot_row.addStretch()
        rand_layout.addLayout(rot_row)
        self.align_cb = QtWidgets.QCheckBox("Align to Surface Normal")
        self.align_cb.setChecked(True)
        rand_layout.addWidget(self.align_cb)
        scroll_layout.addWidget(rand_group)

        # actions
        act_group  = QtWidgets.QGroupBox("Actions")
        act_layout = QtWidgets.QVBoxLayout(act_group)
        undo_btn  = QtWidgets.QPushButton("Undo Last Stroke")
        clear_btn = QtWidgets.QPushButton("Clear All Scattered")
        close_btn = QtWidgets.QPushButton("Close Tool")
        undo_btn.clicked.connect(lambda: cmds.undo())
        clear_btn.clicked.connect(self._clear_all)
        close_btn.clicked.connect(self.close)
        act_layout.addWidget(undo_btn)
        act_layout.addWidget(clear_btn)
        act_layout.addWidget(close_btn)
        scroll_layout.addWidget(act_group)

        scroll_layout.addStretch()
        self.setWidget(root)

    # functions

    def _set_mode(self, mode):
        self.mode = mode
        self.paint_btn.setChecked(mode == "paint")
        self.erase_btn.setChecked(mode == "erase")

    def _toggle_brush(self, active):
    global _ui_ref
    if active:
        _ui_ref = self
        activate_context()
        self.activate_btn.setText("Deactivate Brush")
        self.status_lbl.setText("● ACTIVE — click/drag on any mesh")
    else:
        deactivate_context()
        self.activate_btn.setText("Activate Brush")
        self.activate_btn.setChecked(False)
        self.status_lbl.setText("● Brush inactive")

    def _add_sel(self):
        sel = cmds.ls(selection=True, long=False) or []
        existing = {self.source_list.item(i).text()
                    for i in range(self.source_list.count())}
        for obj in sel:
            if obj not in existing:
                self.source_list.addItem(obj)
        if not sel:
            cmds.warning("Nothing selected.")

    def _refresh(self):
        self.source_list.clear()
        for m in cmds.ls(type="transform", long=False) or []:
            if cmds.listRelatives(m, shapes=True, type="mesh"):
                self.source_list.addItem(m)

    def _remove_src(self):
        for item in self.source_list.selectedItems():
            self.source_list.takeItem(self.source_list.row(item))

    def _clear_all(self):
        ans = QtWidgets.QMessageBox.question(
            self, "Clear All", "Delete ALL scattered instances?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans == QtWidgets.QMessageBox.Yes:
            if cmds.objExists("scatter_grp"):
                kids = cmds.listRelatives("scatter_grp", children=True) or []
                if kids:
                    cmds.delete(kids)

    def get_selected_sources(self):
        sel = self.source_list.selectedItems()
        if sel:
            return [i.text() for i in sel]
        return [self.source_list.item(i).text()
                for i in range(self.source_list.count())]


def show():
    mw  = get_maya_main_window()
    win = ScatterBrushUI(parent=mw)
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, win)
    win.show()

show()



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