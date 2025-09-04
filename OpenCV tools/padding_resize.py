# Padding video to match the common video ratio
# Read Videos under a dir
# Assume input video resolution is smaller than desire resolution
# Padding to fit 16:9 or 4:3 automatically
# Padding will be in the right and/or botton

import os
import cv2
import ffmpeg

# Constants
ratio16to9 = 1.777777
ratio4to3 = 1.333333
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

print("Padding video to match the common video ratio. Notice that the video resolution should close to either 16:9 or 4:3")
print("Padding will be in the right and/or botton")

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

    vidoe_ratio = width / height

    # Video ratio close 16:9
    if abs(vidoe_ratio - ratio16to9) < abs(vidoe_ratio - ratio4to3):
        print("Padding video to fit 16:9...")

        if width % 16 != 0:
            width_out = ((width // 16) + 1) * 16
        else:
            width_out = width
        if height % 9 != 0:
            height_out = ((height // 9) + 1) * 9
        else:
            height_out = height

        if width_out - width > 16:
            print("Input video width error")
            continue
        elif height_out - height > 9:
            print("Input video height error")
            continue
    else: # Video ratio close 4:3
        print("Padding video to fit 4:3...")

        if width % 4 != 0:
            width_out = ((width // 4) + 1) * 4
        else:
            width_out = width
        if height % 3 != 0:
            height_out = ((height // 3) + 1) * 3
        else:
            height_out = height

        if width_out - width > 4:
            print("Input video width error")
            continue
        elif height_out - height > 3:
            print("Input video height error")
            continue


    right = int(width_out - width)
    bottom = int(height_out - height)

    video_path = os.path.join(output_path, mp4_file)
    vout = cv2.VideoWriter(filename=video_path, fourcc=fourcc, fps=fps, frameSize=(width_out, height_out), isColor=True)

    # Start padding frame by frame
    while True:
        ret, frame = vcap.read()            
        if not ret:
            print("frame ended. Exiting")
            break
            
        pad_frame = cv2.copyMakeBorder(frame, top=0, bottom=bottom, left=0, right=right, borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])
        vout.write(pad_frame)

    vcap.release()
    vout.release()

    # ffmpeg paste the audio
    result_path = video_path.replace(".mp4", "_padded.mp4")
    fvideo = ffmpeg.input(video_path)
    faudio = ffmpeg.input(audio_path)
    ffmpeg.concat(fvideo, faudio, v=1, a=1).output(result_path).run(overwrite_output=True)

