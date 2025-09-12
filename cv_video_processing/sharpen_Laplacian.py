# sharpen image by Unsharp Masking
# https://en.wikipedia.org/wiki/Unsharp_masking
# https://www.idtools.com.au/unsharp-masking-with-python-and-opencv/
# Version 1.2

import os
import cv2
import numpy as np
from scipy.ndimage import median_filter
import ffmpeg

# Constants
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
shapred_strength = 0.8
filter_size = 3

# Functions
def unsharp_mask(image, size, strength):

    uimage = cv2.UMat(image)

    # Median filtering
    uimage_mf = median_filter(uimage, size)

    # Calculate the Laplacian
    ulap = cv2.Laplacian(uimage_mf,cv2.CV_64F)

    # Calculate the sharpened image
    usharped = uimage - strength * ulap

    # Saturate the pixels in either direction
    usharped[usharped > 255] = 255
    usharped[usharped < 0] = 0
    
    sharped = cv2.UMat.get(usharped)

    return sharped

print("Sharpen the video with Unsharped Mask Algorithm")

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
    # audio_path = video_path.replace("mp4", "mp3")
    # fvideo = ffmpeg.input(video_path)
    # ffmpeg.output(fvideo, audio_path).run()

    width  = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vcap.get(cv2.CAP_PROP_FPS)
    frame_count = vcap.get(cv2.CAP_PROP_FRAME_COUNT)
    finished_count = 0

    video_path = os.path.join(output_path, mp4_file)
    vout = cv2.VideoWriter(filename=video_path, fourcc=fourcc, fps=fps, frameSize=(width, height), isColor=True)

    # Start padding frame by frame
    while True:
        ret, frame = vcap.read()            
        if not ret:
            print("\nframe ended. Exiting")
            break
            
        sharped_frame = np.zeros_like(frame)
        for i in range(3):
            sharped_frame[:,:,i] = unsharp_mask(frame[:,:,i], filter_size, shapred_strength)
        vout.write(sharped_frame)
        finished_count += 1
        print("\r frame({}/{})".format(finished_count, frame_count), end='')

    vcap.release()
    vout.release()

    # ffmpeg paste the audio
    # result_path = video_path.replace(".mp4", "_sharped.mp4")
    # fvideo = ffmpeg.input(video_path)
    # faudio = ffmpeg.input(audio_path)
    # ffmpeg.concat(fvideo, faudio, v=1, a=1).output(result_path).run(overwrite_output=True)