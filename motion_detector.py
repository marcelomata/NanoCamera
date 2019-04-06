# import the necessary packages
from imutils.video import VideoStream
import numpy as np
import argparse
import datetime
import imutils
import time
import cv2
from dist_functions import *
from dist import *

# CONSTANTS
# idle-use state constants
IDLE = "idle"
MAYBE_USE = "maybe_use"
IN_USE = "in_use"
MAYBE_IDLE = "maybe_idle"

# FUNCTIONS

# probability functions
def obs_model(state):
    if state == IDLE:
        triangle = triangle_dist(0, 2)
        uni = uniform_dist(range(4))
        return mixture(triangle, uni, .9)
    elif state == MAYBE_USE:
        triangle = triangle_dist(1, 2)
        uni = uniform_dist(range(4))
        return mixture(triangle, uni, .6)
    elif state == IN_USE:
        triangle = triangle_dist(2, 2)
        uni = uniform_dist(range(4))
        return mixture(triangle, uni, .9)
    elif state == MAYBE_IDLE:
        triangle = triangle_dist(3, 2)
        uni = uniform_dist(range(4))
        return mixture(triangle, uni, .6)
    else:
        return uniform_dist(range(4))
    
def update_prior(prior, peaks):
    for peak in peaks:
        prior = bayes_rule(prior, obs_model, sum(peak))
    return prior

# Compare before and after tool use images 
def compare_before_after(before_img, after_img):
	# process difference between before and after images
	frame, text, frameDelta, thresh = motion_draw(before_img, after_img)
	print("Compare DONE")
	
	# draw the text and timestamp on the frame
	# concatenate with "before" image
	# horizontal = np.concatenate((before_img, frame), axis = 1)
	cv2.putText(frame, "After session snapshot", (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame and record if the user presses a key
	cv2.imshow("After session snapshot", frame)


# process img, compare to first_img, draw bounding boxes
# Returns: 
def motion_draw(first_img, frame):
	# resize the frame, convert it to grayscale, and blur it
	text = 'Unoccupied'
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the first frame is None, initialize it
	if first_img is None:
		return (gray,)

	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(first_img, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it = no motion detected
		if cv2.contourArea(c) < args["min_area"]:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"

	return (frame, text, frameDelta, thresh)

def motion_boolean(first_img, frame):
	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	first_img = imutils.resize(first_img, width=500)
	gray_prior = cv2.cvtColor(first_img, cv2.COLOR_BGR2GRAY)
	gray_prior = cv2.GaussianBlur(gray_prior, (21, 21), 0)

	frameDelta = cv2.absdiff(gray_prior, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	cnts_count = 0
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it = no motion detected
		if cv2.contourArea(c) < args["min_area"]:
			continue
		cnts_count += 1

	print("cnts:", cnts_count)

	return cnts_count > 2

# MAIN

# ARGUMENTS SETUP
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# VIDEO SOURCE SETUP
# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)
# otherwise, we are reading from a video file
else:
	vs = cv2.VideoCapture(args["video"])
# initialize the first frame in the video stream
firstFrame = None
firstFrameColor = None
priorFrame = None

# IDLE-USE STATE SETUP
ticks = 0
alpha_use = 10
alpha_idle = 10
state = IDLE

# loop over the frames of the video
while True:
	ticks += 1

	# grab the current frame and initialize the occupied/unoccupied
	# text
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	text = "Unoccupied"

	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if frame is None:
		break
	# save colored frame copies
	if firstFrameColor is None:
		firstFrameColor = frame
	frameColor = frame #TODO reference or copy? needed? 

	# process images 
	# 1) detect disturbance from initialization (for drawing boxes)
	motion_result = motion_draw(firstFrame, frame)
	# initialize first frame...
	if len(motion_result) == 1:
		firstFrame = motion_result[0]
		priorFrame = frame
		continue
	# or continue processing
	else:
		frame, text, frameDelta, thresh = motion_result
	# 2) detect difference from previous frame (for detecting motion difference)
		is_motion = motion_boolean(priorFrame, frame)

	# if text == occupied, motion detected 
	if is_motion:
		# if idle, enter maybe use state
		if state == IDLE:
			state = MAYBE_USE
			print("MAYBE_USE")
			ticks = 0
		# if maybe use, check tick count
		elif state == MAYBE_USE:
			if ticks > alpha_use:
				state = IN_USE
				ticks = 0
				print("IN_USE")
		# if maybe idle, go back to in use 
		elif state == MAYBE_IDLE:
			state = IN_USE
			print("IN_USE")
			ticks = 0
	# if text != occupied, no motion detected
	else:
		# if maybe idle, check tick count
		if state == MAYBE_IDLE:
			if ticks > alpha_idle:
				state = IDLE
				ticks = 0
				compare_before_after(firstFrame, frameColor)
				print("Session ended")
		# if maybe use, go back to idle
		elif state == MAYBE_USE:
			state = IDLE
			print("IDLE")
			ticks = 0
		# if in use, enter maybe idle state
		elif state == IN_USE:
			state = MAYBE_IDLE
			print("MAYBE_IDLE")
			ticks = 0
		
	# draw the text and timestamp on the frame
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame and record if the user presses a key
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF

	# set new priorFrame for next frame iteration
	priorFrame = frame

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()


#### NOTES ####
# tune cv2.threshold and --min-area for lighting in this room
