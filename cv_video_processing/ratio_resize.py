# Some of the video downloaded will have strange ratio of 3:2
# Resize the video frames into 16:9 or 4:3 (user selected)
# Version 1.2

import os
import cv2
import ffmpeg

# Constants
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

print("Resize video to match selected ratio (16:9 or 4:3)")
print("pivot is the width or height depends on which one can be fully divided, shrink the other one accordingly")

input_ratio = input("Select 0:(16:9), 1:(4:3) : ")
if input_ratio == '0':
    print("Resize to 16:9!")
elif input_ratio == '1':
    print("Resize to 4:3!")
else:
    print("error : enter 0 or 1!")
    exit()

print("Input top directory for both inputs and outputs")
input_dir = input("input directory : ")

input_path = os.path.join(os.getcwd(), input_dir)
if not os.path.exists(input_path) :
    print("error : input directory : {} not exist".format(input_path))
    exit()

files = os.listdir(input_path)
print("-" * 64)
print("The total number of files in the directory : " + str(len(files)))
print("-" * 64 + "\n\n")

print("-" * 64)
mp4_files = [x for x in files if x.endswith(".mp4")]
print("The total number of .mp4 files in the directory : " + str(len(mp4_files)))
print("-" * 64 + "\n\n")

output_dir = input("output directory : ")

output_path = os.path.join(os.getcwd(), output_dir)
if not os.path.exists(output_path) :
    print("error : input directory : {} not exist".format(output_path))
    print("Create dir on " + output_path)
    os.makedirs(output_path)

for mp4_file in mp4_files:
    video_path = os.path.join(input_path, mp4_file)
    vcap = cv2.VideoCapture(video_path)  
    if not vcap.isOpened():
        print("fail to open Video file : {}\nSkipped".format(mp4_file))
        fail_count += 1
        vcap.release()
        continue
    
    # ffmpeg copy the audio
    audio_path = video_path.replace("mp4", "mp3")
    fvideo = ffmpeg.input(video_path)
    ffmpeg.output(fvideo, audio_path).run()

    width  = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vcap.get(cv2.CAP_PROP_FPS)
    frame_count = vcap.get(cv2.CAP_PROP_FRAME_COUNT)
    finished_count = 0

    if input_ratio == '0':
        print("Resize video to fit 16:9...")

        if height % 9 != 0 and width % 16 != 0:
            print("error : both height and width not fitting as pivot point")
        
        if height % 9 == 0:
            height_out = height
            width_out = int((height / 9) * 16)
            print("New resolution ({}, {})".format(width_out, height_out))
        else:
            width_out = width
            height_out = int((width / 16) * 9)
            print("New resolution ({}, {})".format(width_out, height_out))
    else:
        print("Resize video to fit 4:3...")

        if height % 3 != 0 and width % 4 != 0:
            print("error : both height and width not fitting as pivot point")
        
        if height % 3 == 0:
            height_out = height
            width_out = int((height / 3) * 4)
            print("New resolution ({}, {})".format(width_out, height_out))
        else:
            width_out = width
            height_out = int((width / 4) * 3)
            print("New resolution ({}, {})".format(width_out, height_out))

    video_path = os.path.join(output_path, mp4_file)
    vout = cv2.VideoWriter(filename=video_path, fourcc=fourcc, fps=fps, frameSize=(width_out, height_out), isColor=True)

    # Start padding frame by frame
    while True:
        ret, frame = vcap.read()            
        if not ret:
            print("\nframe ended. Exiting")
            break
            
        resize_frame = cv2.resize(frame, (width_out, height_out), interpolation=cv2.INTER_AREA)
        vout.write(resize_frame)
        finished_count += 1
        print("\r frame({}/{})".format(finished_count, frame_count), end='')

    vcap.release()
    vout.release()

    # ffmpeg paste the audio
    result_path = video_path.replace(".mp4", "_resized.mp4")
    fvideo = ffmpeg.input(video_path)
    faudio = ffmpeg.input(audio_path)
    ffmpeg.concat(fvideo, faudio, v=1, a=1).output(result_path).run(overwrite_output=True)