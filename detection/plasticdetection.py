# USAGE
# python detection/plasticdetection.py --input path/to/input/video --output path/to/output/video --confidence (value from 0 to 1)

# import the necessary packages
import numpy as np
import argparse
from cv2 import cv2
from pyimagesearch.centroidtracker import CentroidTracker

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--confidence", type=float, default=0.80,
    help="minimum probability to filter weak detections")
ap.add_argument("-o", "--output", default="videos/output012.avi",
    help="path to output video file")
ap.add_argument("-f", "--fps", type=int, default=30,
    help="FPS of output video")
ap.add_argument("-co", "--codec", type=str, default="XVID",
    help="codec of output video")
ap.add_argument("-i", "--input", default="videos/captured012.mp4",
    help="path to input video file")
args = vars(ap.parse_args())

# initialize the list of class labels that our model was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = [ " ", "bead", "fiber", "size" ]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# declare the centroid tracker class used for tracking objects
ct = CentroidTracker()

# load our trained tensorflow model
print("[INFO] loading model...")
net = cv2.dnn.readNetFromTensorflow('models/frozen_inference_graph.pb', 'models/new_label_map.pbtxt')

# initialize and preprocess the input video
print("[INFO] starting video...")
vs = cv2.VideoCapture(args["input"])
fourcc = cv2.VideoWriter_fourcc(*args["codec"])
writer = None

# loop over the frames from the video stream
while(vs.isOpened()):

    # grab the frame from the video and resize it
    # to have a maximum width of 400 pixels
    ret,frame = vs.read()

    if writer is None:
        w = vs.get(3)
        h = vs.get(4)
        w = int(w)
        h = int(h)
        writer = cv2.VideoWriter(args["output"], fourcc, args["fps"], (w, h), True)
		
    # if frame is read successfully
    if ret == True:

        # turn frame into blob for analysis
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True)
        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        # push the frame through the model
        detections = net.forward()
    
        rects = []
        indexes = []

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > args["confidence"]:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1]) 
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                rects.append(box.astype("int"))
                indexes.append(idx)
                (startX, startY, endX, endY) = box.astype("int")

                label = "{}: {:.2f}%".format(CLASSES[idx],
                    confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                    COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

        # update the centroid tracker
        objects = ct.update(rects, indexes)

        # loop over the tracked objects
        for (objectID, centroid) in objects.items():
            # draw both the ID of the object and the centroid of the
            # object on the output frame
            text = "ID {}".format(objectID)
            cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

        # write the frame and the boxes to the output video
        writer.write(frame)

	    # show the output frame
        cv2.imshow("Plastic Detection", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
    else:
        break


# grab bounding box lengths, heights, and indices from the centroid tracker
lengths = ct.getLengths()
heights = ct.getHeights()
indices = ct.getIndexes()

beadDiameters = {}
fiberLengths = {}
totalBeads = 0
totalFibers = 0
sizeFlag = 0

# standard scale pixel size for our tests
# THIS CAN BE CHANGED TO WHATEVER YOU NEED
size = 137

# loop through all of the tracked objects
for key,value in indices.items():

    # if the tracked object is a bead
    if value == 1:
        totalBeads = totalBeads + 1
        # save the value of it's bounding box length as it's diameter
        beadDiameters[key] = int(lengths[key][0])
    # if the tracked object is a bead
    if value == 2:
        totalFibers = totalFibers + 1
        # save the value of it's bounding box length as it's length
        fiberLengths[key] = int(lengths[key][0])

print("[INFO] video ended...")

# output the total counts
print("Total detections: ", ct.getNextID())
print("Total beads: ", totalBeads)
print("Total fibers: ", totalFibers)

# output the individual lengths and diameters in real dimensions.
# THIS CAN BE ADJUSTED FOR DIFFERENT UNITS
for key, value in fiberLengths.items():
    print("Length of Fiber ", key, " = ", int(value*500/size), " um")
for key, value in beadDiameters.items():
    print("Diameter of Bead", key, " = ", int(lengths[key][0]*500/size), " um")

# do a bit of cleanup
vs.release()
writer.release()
cv2.destroyAllWindows()