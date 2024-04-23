try:
    from moviepy.editor import *
except:
    print("Warning: Moviepy not installed")
import os
from pathlib import Path
import json

def Generate_Output_Video(self, from_layer = 1, until_layer = "end"):

    print("Generating Output Video...")

    os.chdir(self.Output_Path)

    file = open('jsonData.json', 'r')
    dict_var_of_json = json.load(file)
    file.close()

    layer_thickness=dict_var_of_json['layer_thickness']
    component_dimensions=dict_var_of_json['component_dimensions']

    

    if until_layer=="end":
        n_layers=round(component_dimensions[2]/layer_thickness)
        until_layer=n_layers


    os.system(f"abaqus cae noGUI={ str( self.module_path / f'Generate_animation_files_for_each_job.py -- {from_layer} {until_layer}' ) }")  #Create Individual Videos

    #Concatenate Videos
    clips=[]
    # for i in range(1,int(n_layers)+1): #THIS IS THE CORRECT ONE
    for i in range(from_layer,until_layer+1):
        clip = VideoFileClip( "Video_layer_{}.avi".format(i) ) #5 seconds video
        clips.append(clip)

    final_video= concatenate_videoclips(clips)

    slowed_video = final_video.fx( vfx.speedx, 0.5)
    # resized_video=slowed_video.resize( (1080,720) )

    # resized_video.write_videofile("Merged_Videos.mp4")

    slowed_video.write_videofile("Merged_Videos.mp4")

    os.chdir(self.user_path)

