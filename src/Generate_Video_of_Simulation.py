from moviepy.editor import *
import json
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("../data_09_mm/")

file = open('.\jsonData.json', 'r')
dict_var_of_json = json.load(file)
file.close()

layer_thickness=dict_var_of_json['layer_thickness']
component_dimensions=dict_var_of_json['component_dimensions']

n_layers=component_dimensions[2]/layer_thickness


os.system("abaqus cae noGUI=../src/Generate_animation_files_for_each_job.py -- {}".format(int(n_layers)))  #Create Individual Videos

#Concatenate Videos
clips=[]
for i in range(1,int(n_layers)+1):
    clip = VideoFileClip( "./Video_layer_{}.avi".format(i) ) #5 seconds video
    clips.append(clip)

final_video= concatenate_videoclips(clips)

slowed_video = final_video.fx( vfx.speedx, 0.5)
resized_video=slowed_video.resize( (1080,720) )

resized_video.write_videofile("./Merged_Videos.mp4")

