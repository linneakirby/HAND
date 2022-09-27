import cv2

from skimage.io import imread, imshow
from skimage.color import rgb2gray, rgb2hsv
from skimage.measure import label, regionprops, regionprops_table
from skimage.filters import threshold_otsu
from scipy.ndimage import median_filter
from matplotlib.patches import Rectangle

#adapted from https://learnopencv.com/blob-detection-using-opencv-python-c/
def getBlobs():
    # Read image
    im = cv2.imread(FIG_PATH, cv2.IMREAD_GRAYSCALE)

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 10
    params.maxThreshold = 200


    # Filter by Area.
    params.filterByArea = True
    params.minArea = 1500

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.1

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.87
        
    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01

    # Create a detector with the parameters
    ver = (cv2.__version__).split('.')
    if int(ver[0]) < 3 :
        detector = cv2.SimpleBlobDetector(params)
    else : 
        detector = cv2.SimpleBlobDetector_create(params)


    # Detect blobs.
    keypoints = detector.detect(im)
    print("keypoints")
    print(keypoints)

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
    # the size of the circle corresponds to the size of blob
    if(keypoints):
        im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # Show blobs
        cv2.imshow("Keypoints", im_with_keypoints)
        cv2.waitKey(0)


#adapted from https://learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/
def getBlobs2():
    # read image through command line
    img = cv2.imread(FIG_PATH)

    # convert the image to grayscale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Grayscale", gray_image)
    # cv2.waitKey(0)

    # convert the grayscale image to binary image
    ret, thresh = cv2.threshold(gray_image,127,255,0)

    # find contours in the binary image
    # im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    im2, contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        # calculate moments for each contour
        M = cv2.moments(c)

        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv2.circle(img, (cX, cY), 5, (255, 255, 255), -1)
        cv2.putText(img, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # display the image
        cv2.imshow("Image", img)
        cv2.waitKey(0)


# adapted from https://towardsdatascience.com/image-processing-with-python-blob-detection-using-scikit-image-5df9a8380ade
def generateMask(path):
    image = imread(path)
    imshow(image);

    hsv = rgb2hsv(image[:,:,0:3])
    plt.imshow(hsv[:,:,0], cmap='hsv')

    lower_mask = hsv [:,:,2] > 0.80 #2 represents blue in rgb colorspace
    upper_mask = hsv [:,:,2] <= 1.00
    mask = upper_mask*lower_mask
    red = image[:,:,0]*mask
    green = image[:,:,1]*mask
    blue = image[:,:,2]*mask
    image_mask = np.dstack((red,green,blue))
    imshow(image_mask)