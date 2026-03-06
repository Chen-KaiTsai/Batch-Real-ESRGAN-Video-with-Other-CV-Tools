import PyNvVideoCodec as nvc
import py3nvml as pynvml
import os

# Configurations
gpu_id = 0

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

for mp4_file in mp4_files :
    file_input_path = os.path.join(input_path, mp4_file)
    file_output_path = os.path.join(output_path, mp4_file)
    nv_dmx = nvc.CreateDemuxer(filename=file_input_path, gpuid=gpu_id)

    width = nv_dmx.Width()
    height = nv_dmx.Height()
    codec_from = nv_dmx.GetNvCodecId()

    if width <= 4096 and height <= 4096 :
        print("Hardware Transcoding is allowed on " + mp4_file)
        deviceCount = pynvml.nvidia_smi.nvmlDeviceGetCount()
        gpu_id = input("Choose GPU to Work on :")
        if gpu_id >= deviceCount : 
            print("GPU id out of bound.")
            exit()
        nv_dec = nvc.CreateDecoder(codec=codec_from, usedevicememory=True)

        print(nvc.GetEncoderCaps())

        nv_enc = nvc.CreateEncoder(width=width, height=height, fmt="YUV420", usecpuinputbuffer=True, codec_id="h264")

        with open(file_output_path, 'wb') as f :
            for packet in nv_dmx:
                dec_surfaces = nv_dec.Decode(packet)

                for surface in dec_surfaces:
                    enc_packets = nv_enc.Encode(surface)

                    for enc_packet in enc_packets :
                        f.write(bytes(enc_packet))

            enc_packets = nv_enc.Flush()
            for enc_packet in enc_packets:
                f.write(bytes(enc_packet))
    else :
        print("Hardware Transcoding is not allowed on " + mp4_file + ". Fall back to software Decoding.")
        print("Transcode video to H264 codec with half of the resolution to avoid reaching limitation of the codec")

        width_half = width // 2
        height_half = height // 2
        
        cmd = "ffmpeg -i \"" + file_input_path + "\" -s " + str(width_half) + "x" + str(height_half) + " -c:a copy \"" + file_output_path + "\""
        print("CMD : ", cmd)
        os.system(cmd)
