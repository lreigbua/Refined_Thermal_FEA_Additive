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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=197.076, 
        farPlane=274.327, width=190.606, height=89.6904, cameraPosition=(49.8035, 
        -94.8567, 207.385), cameraUpVector=(0.0377302, 0.995119, 0.0911809), 
        cameraTarget=(24.7439, 5.00179, -5.98566))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=182.157, 
        farPlane=287.919, width=176.177, height=82.9009, cameraPosition=(-43.5518, 
        -134.109, 173.045), cameraUpVector=(0.246583, 0.901556, 0.355517), 
        cameraTarget=(25.2229, 5.20318, -5.80947))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=192.305, 
        farPlane=277.772, width=47.6768, height=22.4345, viewOffsetX=-16.7925, 
        viewOffsetY=-1.11813)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=186.542, 
        farPlane=285.268, width=46.2481, height=21.7622, cameraPosition=(-55.8405, 
        -163.662, 140.541), cameraUpVector=(-0.0549639, 0.875802, 0.479532), 
        cameraTarget=(24.4462, 8.83485, -0.617296), viewOffsetX=-16.2893, 
        viewOffsetY=-1.08463)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.702, 
        farPlane=275.502, width=46.5358, height=21.8976, cameraPosition=(1.20955, 
        -189.848, 118.58), cameraUpVector=(0.152205, 0.774121, 0.614467), 
        cameraTarget=(25.9213, 8.3906, -8.76842), viewOffsetX=-16.3906, 
        viewOffsetY=-1.09138)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=190.018, 
        farPlane=273.187, width=13.6669, height=6.43102, viewOffsetX=-19.8899, 
        viewOffsetY=0.408125)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=186.997, 
        farPlane=277.721, width=13.4496, height=6.32878, cameraPosition=(-8.80259, 
        -205.435, 88.3485), cameraUpVector=(0.0819667, 0.677391, 0.731042), 
        cameraTarget=(26.2382, 8.94571, -6.20306), viewOffsetX=-19.5737, 
        viewOffsetY=0.401636)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.554, 
        farPlane=277.164, width=5.67274, height=2.66933, viewOffsetX=-19.8472, 
        viewOffsetY=1.0745)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.264, 
        farPlane=279.092, width=5.66395, height=2.66519, cameraPosition=(-17.5351, 
        -204.185, 89.8635), cameraUpVector=(0.102849, 0.679377, 0.726546), 
        cameraTarget=(26.2319, 7.98284, -6.03271), viewOffsetX=-19.8164, 
        viewOffsetY=1.07284)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.238, 
        farPlane=279.118, width=5.66316, height=2.66482, viewOffsetX=-19.64, 
        viewOffsetY=1.23079)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=185.984, 
        farPlane=287.801, width=5.62522, height=2.64697, cameraPosition=(-58.0022, 
        -198.177, 86.3315), cameraUpVector=(0.162508, 0.654647, 0.738261), 
        cameraTarget=(25.6937, 4.02413, -4.42387), viewOffsetX=-19.5085, 
        viewOffsetY=1.22254)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=186.011, 
        farPlane=287.774, width=4.97117, height=2.3392, viewOffsetX=-18.5385, 
        viewOffsetY=1.42363)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=186.117, 
        farPlane=286.202, width=4.974, height=2.34054, cameraPosition=(-49.64, 
        -200.196, 86.9113), cameraUpVector=(0.105901, 0.669643, 0.735094), 
        cameraTarget=(26.0924, 5.19588, -3.67416), viewOffsetX=-18.5491, 
        viewOffsetY=1.42444)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.101, 
        farPlane=280.917, width=5.0003, height=2.35291, cameraPosition=(-24.4019, 
        -203.717, 89.8111), cameraUpVector=(0.0739431, 0.681882, 0.727715), 
        cameraTarget=(26.6901, 7.42894, -4.70907), viewOffsetX=-18.6472, 
        viewOffsetY=1.43197)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=186.995, 
        farPlane=281.024, width=6.83729, height=3.21732, viewOffsetX=-19.0827, 
        viewOffsetY=1.59726)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.647, 
        farPlane=277.184, width=6.86111, height=3.22852, cameraPosition=(-6.61466, 
        -207.206, 85.117), cameraUpVector=(0.0925211, 0.665701, 0.740461), 
        cameraTarget=(26.6763, 8.71645, -6.51405), viewOffsetX=-19.1492, 
        viewOffsetY=1.60282)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.703, 
        farPlane=277.128, width=6.00364, height=2.82504, viewOffsetX=-20.3394, 
        viewOffsetY=1.56597)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.707, 
        farPlane=277.123, width=6.00378, height=2.8251, cameraPosition=(-6.55305, 
        -207.004, 85.6161), cameraUpVector=(0.0725044, 0.668618, 0.740063), 
        cameraTarget=(26.7379, 8.91875, -6.01496), viewOffsetX=-20.3399, 
        viewOffsetY=1.566)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.439, 
        farPlane=277.503, width=5.99521, height=2.82107, cameraPosition=(-7.50972, 
        -208.214, 82.5209), cameraUpVector=(0.0568199, 0.658691, 0.750265), 
        cameraTarget=(26.7851, 9.02972, -5.54734), viewOffsetX=-20.3109, 
        viewOffsetY=1.56377)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.382, 
        farPlane=277.559, width=6.37594, height=3.00022, viewOffsetX=-20.0374, 
        viewOffsetY=1.5803)
    
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
