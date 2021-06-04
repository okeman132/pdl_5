
import cv2
import base64
from align_custom import AlignCustom
from face_feature import FaceFeature
from mtcnn_detect import MTCNNDetect
from connect import CONNECTION
from tf_graph import FaceRecGraph
import argparse
import sys
import json
import time
import numpy as np

TIMEOUT = 10 #10 seconds

def main(args):
    mode = args.mode
    if(mode == "camera"):
        camera_recog()
    elif mode == "input":
        create_manual_data();
    else:
        raise ValueError("Unimplemented mode")
'''
Description:
Images from Video Capture -> detect faces' regions -> crop those faces and align them 
    -> each cropped face is categorized in 3 types: Center, Left, Right 
    -> Extract 128D vectors( face features)
    -> Search for matching subjects in the dataset based on the types of face positions. 
    -> The preexisitng face 128D vector with the shortest distance to the 128D vector of the face on screen is most likely a match
    (Distance threshold is 0.6, percentage threshold is 70%)
    
'''
def camera_recog():
    print("[INFO] camera sensor warming up...")
    vs = cv2.VideoCapture(0); #get input from webcam
    detect_time = time.time()
    Test = 0
    while True:
        _,frame = vs.read();
        rects, landmarks = face_detect.detect_face(frame,80);#min face size is set to 80x80
        aligns = []
        positions = []  #Center || Left || Right
        for (i, rect) in enumerate(rects):
            aligned_face, face_pos = aligner.align(160,frame,landmarks[:,i])
            if len(aligned_face) == 160 and len(aligned_face[0]) == 160:
                aligns.append(aligned_face)
                positions.append(face_pos)
            else: 
                print("Align face failed") #log
        if(len(aligns) > 0):
            features_arr = extract_feature.get_features(aligns)
            recog_data = findPeople(features_arr,positions)
            for (i,rect) in enumerate(rects):
                cv2.rectangle(frame,(rect[0],rect[1]),(rect[2],rect[3]),color=(0, 255, 0), thickness=3) #draw bounding box for the face
                cv2.putText(frame,recog_data[i][0]+" - "+str(round(float(recog_data[i][1]),2))+"%",(rect[0],rect[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1,cv2.LINE_AA)
                if(round(float(recog_data[i][1]),2)>75):
                    Test+=1
                    if(Test==10):
                        print('Lại gần để đo nhiệt độ')
                        connection.connectmySQL(recog_data[i][0])
                    Test=Test%10
                        
        cv2.imshow("Frame",frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
'''
facerec_128D.txt Data Structure:
{
"Person ID": {
    "Center": [[128D vector]],
    "Left": [[128D vector]],
    "Right": [[128D Vector]]
    }
}
This function basically does a simple linear search for 
^the 128D vector with the min distance to the 128D vector of the face on screen
'''
def findPeople(features_arr, positions, thres = 0.6, percent_thres = 80):
    '''
     : features_arr: danh sách 128d Đặc điểm của tất cả các khuôn mặt trên màn hình
     : Position: danh sách các loại vị trí khuôn mặt của tất cả các khuôn mặt trên màn hình
     : thres: ngưỡng khoảng cách
     : return: tên người và tỷ lệ phần trăm
    '''
    f = open('./facerec_128D.txt','r')
    data_set = json.loads(f.read());
    returnRes = [];
    for (i,features_128D) in enumerate(features_arr):
        result = "Unknown";
        smallest = sys.maxsize
        for person in data_set.keys():
            person_data = data_set[person][positions[i]];
            for data in person_data:
                distance = np.sqrt(np.sum(np.square(data-features_128D)))
                if(distance < smallest):
                    smallest = distance;
                    result = person;
        percentage =  min(100, 100 * thres / smallest)
        if percentage <= percent_thres :
            result = "Unknown"  
        returnRes.append((result,"%.2f" % (percentage)))
    return returnRes    

'''
Miêu tả:
Người dùng nhập ID của mình -> Hình ảnh từ Quay video -> phát hiện khuôn mặt -> cắt khuôn mặt và căn chỉnh nó
     -> khuôn mặt sau đó được phân loại thành 3 loại: Trung tâm, Trái, Phải
     -> Trích xuất vectơ 128D (tính năng khuôn mặt)
     -> Nối mỗi vectơ 128D khuôn mặt mới được trích xuất vào loại vị trí tương ứng của nó (Trung tâm, Trái, Phải)
     -> Nhấn Q để dừng chụp
     -> Tìm tâm (trung bình) của các vectơ 128D đó trong mỗi loại. (np.mean (...))
     -> Lưu
    
'''
def create_manual_data():
    vs = cv2.VideoCapture(0); #get input from webcam
    print("ID:")
    new_id = input(); #ez python input()
    # print("Name:")
    # new_name = input()
    # print("Age:")
    # new_age = input()
    # print("Sex:")
    # new_sex = input()
    # print("Address:")
    # new_add = input()
    # print("IdFaculty:")
    # new_idF = input()
    f = open('./facerec_128D.txt','r');
    data_set = json.loads(f.read());
    person_imgs = {"Left" : [], "Right": [], "Center": []};
    person_features = {"Left" : [], "Right": [], "Center": []};
    print("Please start turning slowly. Press 'q' to save and add this new user to the dataset");
    while True:
        _, frame = vs.read();
        rects, landmarks = face_detect.detect_face(frame, 80);  # min face size is set to 80x80
        for (i, rect) in enumerate(rects):
            aligned_frame, pos = aligner.align(160,frame,landmarks[:,i]);
            if len(aligned_frame) == 160 and len(aligned_frame[0]) == 160:
                #cv2.rectangle(frame,(rect[0],rect[1]),(rect[2],rect[3]),color=(0, 255, 0), thickness=3) #draw bounding box for the face
                person_imgs[pos].append(aligned_frame)
                cv2.imshow("Captured face", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            scale_percent =  30# percent of original size
            width = int(frame.shape[1] * scale_percent / 100)
            height = int(frame.shape[0] * scale_percent / 100)
            dim = (width, height)
            resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
            cv2.imwrite("dataset/"+new_id+".jpg",resized)
            break
    for pos in person_imgs: #there r some exceptions here, but I'll just leave it as this to keep it simple
        person_features[pos] = [np.mean(extract_feature.get_features(person_imgs[pos]),axis=0).tolist()]
    data_set[new_id] = person_features;
    f = open('./facerec_128D.txt', 'w');
    f.write(json.dumps(data_set))
    with open("dataset/"+str(new_id)+".jpg", "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
    # connection1=CONNECTION();
    # connection1.insert(new_id,new_name,new_age,new_sex,new_add,new_idF,my_string.decode('utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, help="Run camera recognition", default="camera")
    args = parser.parse_args(sys.argv[1:]);
    FRGraph = FaceRecGraph();
    MTCNNGraph = FaceRecGraph();
    aligner = AlignCustom();
    connection=CONNECTION();
    extract_feature = FaceFeature(FRGraph)
    face_detect = MTCNNDetect(MTCNNGraph, scale_factor=2); #scale_factor, rescales image for faster detection
    main(args);
