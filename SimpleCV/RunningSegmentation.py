from SimpleCV.base import *
from SimpleCV.Features import Feature, FeatureSet
from SimpleCV.ImageClass import Image
from SimpleCV.BlobMaker import BlobMaker
from SimpleCV.SegmentationBase import SegmentationBase

import abc


class RunningSegmentation(SegmentationBase):

    mError = False
    mAlpha = 0.1
    mThresh = 10
    mModelImg = None
    mDiffImg = None
    mCurrImg = None
    mBlobMaker = None
    mGrayOnly = True
    mReady = False
    
    def __init__(self, alpha=0.7, thresh=(20,20,20)):
        self.mError = False
        self.mReady = False
        self.mAlpha = alpha
        self.mThresh = thresh
        self.mModelImg = None
        self.mDiffImg = None
        self.mColorImg = None
        self.mBlobMaker = BlobMaker()
 
    def loadSettings(self, file):       
        """
        Load all of the segmentation settings from file
        """
        myFile = open(file,'w')
        myFile.writeline("Running Segmentation Parameters")
        myFile.write(str(self.mThresh))
        myFile.write(str(self.mAlpha))
        myFile.close()
        return
    
    def saveSettings(self, file):
        """
        save all of the segmentation settings from file
        """
        myFile = open(file,'r')
        myFile.readline()
        self.mThresh = myFile.readline()
        self.mAlpha = myFile.readline()
        myFile.close()
        return
    
    def addImage(self, img):
        """
        Add a single image to the segmentation algorithm
        """
        if( img is None ):
            return
        
        self.mColorImg = img 
        if( self.mModelImg == None ):    
            self.mModelImg = Image(cv.CreateImage((img.width,img.height), cv.IPL_DEPTH_32F, 3))          
            self.mDiffImg = Image(cv.CreateImage((img.width,img.height), cv.IPL_DEPTH_32F, 3))           
        else:   
            # do the difference 
            cv.AbsDiff(self.mModelImg.getBitmap(),img.getFPMatrix(),self.mDiffImg.getBitmap())
            #update the model 
            cv.RunningAvg(img.getFPMatrix(),self.mModelImg.getBitmap(),self.mAlpha)
            self.mReady = True
        return
    

    def isReady(self):
        """
        Returns true if the camera has a segmented image ready. 
        """
        return self.mReady

    
    def isError(self):
        """
        Returns true if the segmentation system has detected an error.
        Eventually we'll consruct a syntax of errors so this becomes
        more expressive 
        """
        return self.mError #need to make a generic error checker
    
    def resetError(self):
        """
        Clear the previous error. 
        """
        self.mError = false
        return 

    def reset(self):
        """
        Perform a reset of the segmentation systems underlying data.
        """
        self.mModelImg = None
        self.mDiffImg = None
    
    def getRawImage(self):
        """
        Return the segmented image with white representing the foreground
        and black the background. 
        """
        return self._floatToInt(self.mDiffImg)
    
    def getSegmentedImage(self, whiteFG=True):
        """
        Return the segmented image with white representing the foreground
        and black the background. 
        """
        retVal = None
        img = self._floatToInt(self.mDiffImg)
        if( whiteFG ):
            retVal = img.binarize(thresh=self.mThresh)
        else:
            retVal = img.binarize(thresh=self.mThresh).invert()
        return retVal
    
    def getSegmentedBlobs(self):
        """
        return the segmented blobs from the fg/bg image
        """
        retVal = []
        if( self.mColorImg is not None and self.mDiffImg is not None ):

            eightBit = self._floatToInt(self.mDiffImg)
            retVal = self.mBlobMaker.extractFromBinary(eightBit.binarize(thresh=self.mThresh),self.mColorImg)
 
        return retVal
    
    
    def _floatToInt(self,input):
        """
        convert a 32bit floating point cv array to an int array
        """
        temp = cv.CreateImage((input.width,input.height), cv.IPL_DEPTH_8U, 3) 
        cv.Convert(input.getBitmap(),temp)
   
        return Image(temp) 
    
    