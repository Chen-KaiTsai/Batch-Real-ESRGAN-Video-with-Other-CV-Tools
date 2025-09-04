import os
import cv2
import time

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

print("Model names: 0 : realesr-animevideov3 |  1 : RealESRGAN_x4plus_anime_6B | 2 : RealESRGAN_x4plus | \
3 : RealESRNet_x4plus | 4 : RealESRGAN_x2plus | 5 : realesr-general-x4v3")

model_index = input("select model : ")
if not model_index.isnumeric() :
    print("error : please input an index")
    exit()

if model_index == "0" :
    model_name = "realesr-animevideov3"
elif model_index == "1" :
    model_name = "RealESRGAN_x4plus_anime_6B"
elif model_index == "2" :
    model_name = "RealESRGAN_x4plus"
elif model_index == "3" :
    model_name = "RealESRNet_x4plus"
elif model_index == "4" :
    model_name = "RealESRGAN_x2plus"
elif model_index == "5" :
    model_name = "realesr-general-x4v3"
else :
    print("error : model index out of bound")
    exit()

print("Adjust the final output. Please keep final resolution under 4K")
final_scale = input("enter the final scale : ")
if final_scale.isalpha() :
    print("error : please input an float or int")
    exit()
if float(final_scale) < 1 or float(final_scale) > 4 :
    print("error : scale is out of bound (1, 4)")
    exit()

using_face_enhance = input("Using face enhance model? (y/n)")
if using_face_enhance == "y" or "Y":
    suffix_face_enhance = " --face_enhance"
else:
    suffix_face_enhance = ""

fail_count = 0
for mp4_file in mp4_files :
    video_path = os.path.join(input_path, mp4_file)
    vcap = cv2.VideoCapture(video_path)
    if not vcap.isOpened():
        print("fail to open Video file : {}\nSkipped".format(mp4_file))
        fail_count += 1
        continue
    width  = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = vcap.get(cv2.CAP_PROP_FPS)
    frame_count = vcap.get(cv2.CAP_PROP_FRAME_COUNT)
    print("-" * 64)
    print("Video Size : ({}, {}, {}) FPS : {}".format(width, height, frame_count, fps))
    print("-" * 64 + "\n\n")
    
    print("Start converting Video")
    start = time.time()
    cmd = "python inference_realesrgan_video.py -i \"" + video_path \
        + "\" -o \"" + os.path.join(output_path, mp4_file) + "\" -n " + model_name + " -s " + final_scale + suffix_face_enhance
    print("CMD : ", cmd)
    result = os.system(cmd)
    result >> 8
    if not result == 0 :
        print("error : failed to upscale video file {}".format(mp4_file))
        fail_count += 1
        continue
    end = time.time()

    print("--- %s seconds ---" % (end - start))

print("Failed Count : {}".format(fail_count))
