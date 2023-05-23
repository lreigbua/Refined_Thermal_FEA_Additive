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

    #show only legend
    session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(triad=OFF, 
    title=OFF, state=OFF, annotations=OFF, compass=OFF)
    session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
        legendBackgroundStyle=OTHER, legendBackgroundColor='#FFFFFF')
    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
        CONTOURS_ON_DEF, ))

    #set view
    session.viewports['Viewport: 1'].view.setValues(nearPlane=174.972, 
        farPlane=300.16, width=78.227, height=40.4939, viewOffsetX=-0.965366, 
        viewOffsetY=-2.0014)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=176.539, 
        farPlane=305.144, width=78.9274, height=40.8565, cameraPosition=(141.429, 
        -152.98, 117.266), cameraUpVector=(-0.432047, 0.626291, 0.648918), 
        cameraTarget=(5.10933, 1.70248, -0.751161), viewOffsetX=-0.97401, 
        viewOffsetY=-2.01932)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=186.846, 
        farPlane=294.837, width=12.2697, height=6.35137, viewOffsetX=-3.39546, 
        viewOffsetY=2.30767)
    
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
