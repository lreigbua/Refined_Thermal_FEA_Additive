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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=28.0083, 
        farPlane=55.8498, width=30.1111, height=13.3326, cameraPosition=(-14.6868, 
        -32.6575, 15.4817), cameraUpVector=(0.186149, 0.722938, 0.665364), 
        cameraTarget=(3.28176, -0.382189, -3.74957))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=28.1826, 
        farPlane=55.4385, width=30.2985, height=13.4156, cameraPosition=(-24.6073, 
        -28.785, 8.53758), cameraUpVector=(0.291665, 0.54416, 0.786652), 
        cameraTarget=(3.21484, -0.356067, -3.79641))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=28.0581, 
        farPlane=55.6875, width=30.1646, height=13.3563, cameraPosition=(-18.4257, 
        -29.232, 17.005), cameraUpVector=(0.488858, 0.581627, 0.650176), 
        cameraTarget=(3.23914, -0.357824, -3.76313))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=28.0572, 
        farPlane=55.6716, width=30.1637, height=13.3559, cameraPosition=(-18.1026, 
        -27.1064, 19.9753), cameraUpVector=(0.527418, 0.616416, 0.584689), 
        cameraTarget=(3.24089, -0.346321, -3.74706))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=31.0943, 
        farPlane=52.6345, width=6.6903, height=2.96234, viewOffsetX=-0.32058, 
        viewOffsetY=2.84467)

    
    #make animation
    session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
    numIntervals=10, outsideLimitsAboveColor="Grey60",
    outsideLimitsBelowColor='#0000FF', maxAutoCompute=OFF, maxValue=300.0,
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
