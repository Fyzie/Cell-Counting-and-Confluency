import os
import cv2
import imutils
from pushbullet import Pushbullet
import glob, random, time

# from robotic import *
# init() # initialize robotic arm position

# register email into pushbullet browser
# gmail = curiosity.iium@gmail.com
# psk = procuriosity21

# get access code
pb = Pushbullet("o.iBWH6dXZLIRNdro3pW2y12lu646atxiJ")
print(pb.devices)

# load the model
net = cv2.dnn_DetectionModel("yolov4-tiny-custom.cfg", "yolov4-tiny-custom_best_aug.weights")
net.setInputSize(416, 416)
net.setInputScale(1.0 / 255)
net.setInputSwapRB(True)

# always check if new image exists

while True:
    path = "new/"
    # path = "H:/"
    # path = "/media/pi/4201-21A6/"
    if os.path.exists(path):
        dirs = os.listdir(path)
        if len(dirs) != 0:
            for item in dirs:
                full_path = os.path.join(path, item)
                if os.path.isfile(full_path):
                    select_img = full_path
                    chosen = os.path.basename(select_img)
                    frame = cv2.imread(full_path)
                    h, w, _ = frame.shape
                    frame_size = h * w

                    with open('obj.names', 'r') as f:
                        names = f.read().split('\n')

                    confluency = 0
                    classes, confidence, boxes = net.detect(frame, confThreshold=0.1, nmsThreshold=0.4)
                    for classId, confidence, box in zip(classes.flatten(), confidence.flatten(), boxes):
                        label = '%.2f' % confidence
                        label = '%s:%s' % (names[classId], label)
                        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5, 1)
                        left, top, width, height = box
                        area = width * height
                        confluency += area
                        top = max(top, labelSize[1])
                        cv2.rectangle(frame, box, color=(0, 255, 0), thickness=3)
                        cv2.rectangle(frame, (left, top - labelSize[1]), (left + labelSize[0], top + baseLine),
                                      (255, 255, 255), cv2.FILLED)
                        cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

                    percentage = confluency / frame_size * 100
                    percentage = round(percentage, 2)
                    frame = imutils.resize(frame, width=600)
                    print("Image: ", chosen)
                    num_cell = len(classes.flatten())
                    print('Number of cells: ', num_cell)
                    # print(confidence.flatten())
                    print('Confluency: ', percentage, '%')
                    cv2.imshow(
                        "Image: " + chosen + ' Number of cells: ' + str(num_cell) + ' Confluency: ' + str(percentage) + '%',
                        frame)
                    chosen_name = chosen.split(".")
                    file_name = chosen_name[0] + " N" + str(num_cell) + " P" + str(percentage) + ".jpg"
                    cv2.imwrite("result3/" + file_name, frame)

                    # notify the users through Pushbullet network
                    # for specific devices
                    # dev = pb.devices[0]
                    # push1 = pb.push_note("Alert!!",
                    #                      "Image: " + chosen + "\n" +
                    #                      "Number of cells: " + str(num_cell) + "\n" +
                    #                      "Confluency: " + str(percentage) + "%",
                    #                      device=dev)
                    #
                    # # send processed image
                    # with open("result/" + file_name, "rb") as pic:
                    #     img_file = pb.upload_file(pic, chosen)
                    # push2 = pb.push_file(**img_file, device=dev)

                    # for all registered devices
                    # push1 = pb.push_note("Alert!!",
                    #                      "Image: " + chosen + "\n" +
                    #                      "Number of cells: " + str(num_cell) + "\n" +
                    #                      "Confluency: " + str(percentage) + "%")
                    #
                    # with open("result/" + file_name, "rb") as pic:
                    #     file_data = pb.upload_file(pic, chosen)
                    # push2 = pb.push_file(**file_data)

                    # robotic arm: replace the dish if limit reached
                    # if percentage > 4:
                    #     control()

                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                    os.remove(full_path)
    time.sleep(1)