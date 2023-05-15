from moviepy.editor import *
import json

clips=[]
for i in range(1,43):
    clip = VideoFileClip( "./data/trial{}.avi".format(i) ) #5 seconds video
    clips.append(clip)

final_video= concatenate_videoclips(clips, method="compose")

slowed_video = final_video.fx( vfx.speedx, 0.5)

slowed_video.write_videofile("./video.mp4")

