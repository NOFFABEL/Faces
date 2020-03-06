# coding=utf-8
"""Performs face detection in realtime.

Based on code from https://github.com/shanren7/real_time_face_recognition
"""
# MIT License
#
# Copyright (c) 2017 François Gervais
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import argparse
import sys
import os
import time
import natsort as ns
from IPython.display import HTML
from base64 import b64encode

import cv2
from google.colab.patches import cv2_imshow

import face


def add_overlays(frame, faces, frame_rate):
    if faces is not None:
        for face in faces:
            face_bb = face.bounding_box.astype(int)
            cv2.rectangle(frame,
                          (face_bb[0], face_bb[1]), (face_bb[2], face_bb[3]),
                          (0, 0, 255), 2)
            if face.name is not None:
                cv2.putText(frame, face.name, (face_bb[0], face_bb[3]),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                            thickness=2, lineType=2)

    cv2.putText(frame, str(frame_rate) + " fps", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                thickness=2, lineType=2)

def look(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            with open(os.path.join(root, f), "r") as auto:

def main(args):
    if args.debug:
        print("Debug enabled")
        face.debug = True

    frame_interval = 3  # Number of frames after which to run face detection
    fps_display_interval = 5  # seconds
    frame_rate = 0
    frame_count = 0
    
    video_dir = args.video_dir
    img_dir = 'treated_dir'  
    os.makedirs(img_dir, exist_ok=True)
    
    if os.path.isdir(video_dir):
        files = os.listdir(video_dir):
        for f in files:
            if os.path.isfile(f):
                video_treat(os.path.join(video_dir, f), img_dir)
    else:
        video_treat(video_dir, img_dir)
    
    video_builder(img_dir)
    


def video_treat(video_path, img_dir):
    
    if any(video_path.endswith(x) for x in ('.mp4', '.avi', '.flv')):
        print('File: ###--{}--##'.format(video_path))
        print('START...')
        img_ = 0
        suffix = os.path.basename(video_path).split('.')[0]
        video_capture = cv2.VideoCapture(video_path)
        face_recognition = face.Recognition()
        start_time = time.time()

        while True:
            # Capture frame-by-frame
            ret, frame = video_capture.read()

            if (frame_count % frame_interval) == 0:
                faces = face_recognition.identify(frame)

                # Check our current fps
                end_time = time.time()
                if (end_time - start_time) > fps_display_interval:
                    frame_rate = int(frame_count / (end_time - start_time))
                    start_time = time.time()
                    frame_count = 0
            
            add_overlays(frame, faces, frame_rate)
            
            frame_count += 1
            
            img_name = suffix + '_' + str(img_) + ".png"
            img_path = os.path.join(img_dir, img_name)
            cv2.imwrite(img_path,frame)
            img_ += 1
            
            # this shows frame-by-frame image...
            # cv2_imshow(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything is done, release the capture
        video_capture.release()
        #cv2.destroyAllWindows()
        print('...END')
    else:
        print('Wrong format for {}. Try with a video (.mp4, .avi or .flv) file'.format(video_path))

def video_builder(img_dir):
    fileList = []
    # trie des fames avant composition de la nouvelle vidéo
    fileList =  ns.natsorted(os.listdir(img_dir))
    output = './final_out.mp4'
    
    writer = imageio.get_writer(output, fps=25)
    for f in fileList:
        writer.append_data(imageio.imread(os.path.join(img_dir, f)))
    writer.close()
    mp4 = open(output,'rb').read()
    data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
    HTML("""
    <video width=450 controls>
          <source src="%s" type="video/mp4">
    </video>
    """ % data_url)

def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--debug', action='store_true',
                        help='Enable some debug outputs.')
    parser.add_argument('--video_dir', type=str,
        help='Path to the video or folder input. It can be either a video or a dir containing some videos')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
