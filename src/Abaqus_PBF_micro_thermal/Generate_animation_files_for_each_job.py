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

    #open ODB
    o3 = session.openOdb(name='./Job-layer-'+str(i)+'.odb')
    session.viewports['Viewport: 1'].setValues(displayedObject=o3)
    
    #show deformed state
    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))

    #Don't show mesh:
    session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
        visibleEdges=FEATURE)

    #show only legend
    session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(triad=OFF, 
    title=OFF, state=OFF, annotations=OFF, compass=OFF)
    session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
        legendBackgroundStyle=OTHER, legendBackgroundColor='#FFFFFF')
    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
        CONTOURS_ON_DEF, ))

    #set view
    session.View(name='User-1', nearPlane=219.34, farPlane=238.19, width=39.627, 
        height=10.951, projection=PERSPECTIVE, cameraPosition=(4.92, 4.92, 145.29), 
        cameraUpVector=(0, 1, 0), cameraTarget=(4., 4.92, -4.5), 
        viewOffsetX=1.0332, viewOffsetY=-0.48829, autoFit=OFF)
    session.viewports['Viewport: 1'].view.setValues(session.views['User-1'])
            
    #make animation
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
