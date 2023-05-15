from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *


import sys
import os

# This code opens all the ODBs generated and produces a file of the animation for each

for i in range(1,int(sys.argv[-1])+1):

    o3 = session.openOdb(name='./Job-layer-'+str(i)+'.odb')
    session.viewports['Viewport: 1'].setValues(displayedObject=o3)
    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    UNDEFORMED, ))

    session.viewports['Viewport: 1'].view.setValues(nearPlane=195.222, 
        farPlane=280.316, width=168.733, height=89.3628, cameraPosition=(148.749, 
        3.49794, 184.505), cameraUpVector=(-0.621165, 0.782222, 0.0477852), 
        cameraTarget=(4.72604, 2.02007, -4.70611))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=196.106, 
        farPlane=277.644, width=169.497, height=89.7673, cameraPosition=(60.2546, 
        -68.7546, 215.411), cameraUpVector=(-0.346427, 0.937635, 0.0287877), 
        cameraTarget=(4.73517, 2.02752, -4.7093))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=173.877, 
        farPlane=303.332, width=150.284, height=79.5921, cameraPosition=(182.658, 
        -101.586, 113.828), cameraUpVector=(-0.563687, 0.522895, 0.639404), 
        cameraTarget=(4.26054, 2.15483, -4.3154))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=176.53, 
        farPlane=299.959, width=152.577, height=80.8064, cameraPosition=(143.055, 
        -128.392, 137.985), cameraUpVector=(-0.59594, 0.579259, 0.556161), 
        cameraTarget=(4.12584, 2.06365, -4.23323))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=177.259, 
        farPlane=299.051, width=153.207, height=81.1403, cameraPosition=(132.764, 
        -132.579, 143.652), cameraUpVector=(-0.625615, 0.572712, 0.529723), 
        cameraTarget=(4.10636, 2.05572, -4.2225))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=188.341, 
        farPlane=287.97, width=16.4948, height=8.73582, viewOffsetX=0.788131, 
        viewOffsetY=4.38038)


    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))
    session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
    numIntervals=10, outsideLimitsAboveColor="Grey60",
    outsideLimitsBelowColor='#0000FF', maxAutoCompute=OFF, maxValue=1650.0,
    minAutoCompute=ON, minValue=0.0)
    session.viewports['Viewport: 1'].animationController.setValues(
        animationType=TIME_HISTORY)
    session.viewports['Viewport: 1'].animationController.play(duration=UNLIMITED)
    session.imageAnimationOptions.setValues(vpDecorations=ON, vpBackground=OFF, 
        compass=OFF)
    session.writeImageAnimation(fileName='Video_layer_'+str(i), format=AVI, canvasObjects=(
        session.viewports['Viewport: 1'], ))
    session.viewports['Viewport: 1'].animationController.setValues(
    animationType=NONE)
