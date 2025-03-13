# Enter your code here
import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
import os


ImagePath =None
winname = "BlemishRemover"

def EdgesMatricExtracter (Mat):
    Edgesmat = np.zeros_like(Mat)
    Edgesmat[:,0] = Mat[:,0]
    Edgesmat[0,:] = Mat[0,:]
    Edgesmat[:,-1] = Mat[:,-1]
    Edgesmat[-1,:] = Mat[-1,:]
    return Edgesmat
def Extractneighbour(Source,x,y,r):
    SrC_hieght,Src_width=Source.shape[:2]
    X_Start = max(x-r,0)
    Y_Start = max(y-r,0)
    X_End = min(x+r+1,SrC_hieght)
    Y_End = min(y+r+1,Src_width)
    Neighbourhood = Source[X_Start:X_End,Y_Start:Y_End]
    return Neighbourhood
def BlemishRemover(action, x, y, flags, userdata):
    global source 
    if action == cv2.EVENT_LBUTTONDOWN:
        radii = 30
        while(True):
            BlemishROI = Extractneighbour(source, y, x, radii)  # Ensure (row, col) order
            Boundary_BlemishROI = EdgesMatricExtracter(BlemishROI)
            Boundary_BlemishROI = Boundary_BlemishROI.astype(np.float32) / 255.0 
            candidate_neighbors = []
            ROI_Mask = 255 * np.ones(BlemishROI.shape, BlemishROI.dtype)
            
            for i in range(-5, 6):
                for j in range(-5, 6):
                    if i == 0 or j == 0: continue
                    X_inc = radii * (i / abs(i)) + i
                    Y_inc = radii * (j / abs(j)) + j
                    NewCenter = (y + X_inc, x + Y_inc)  # Maintain correct order
                    New_Nei = Extractneighbour(source, int(NewCenter[0]), int(NewCenter[1]), radii)
                    
                    if New_Nei.shape == BlemishROI.shape:
                        candidate_neighbors.append(New_Nei)
            
            selected_neighbor = None
            Xgradient_BlemishROI = cv2.Sobel(BlemishROI, cv2.CV_32F, 1, 0)
            Ygradient_BlemishROI = cv2.Sobel(BlemishROI, cv2.CV_32F, 0, 1)
            MinX_range = abs(np.max(Xgradient_BlemishROI) - np.min(Xgradient_BlemishROI))
            MinY_range = abs(np.max(Ygradient_BlemishROI) - np.min(Ygradient_BlemishROI))

            for candidate in candidate_neighbors:
                Boundary_candidate = EdgesMatricExtracter(candidate)
                Boundary_candidate = Boundary_candidate.astype(np.float32) / 255.0
                Dist = np.linalg.norm(Boundary_candidate - Boundary_BlemishROI)
                
                if Dist < 1.5:
                    Xgradient_candidate = cv2.Sobel(candidate, cv2.CV_32F, 1, 0)
                    Ygradient_candidate = cv2.Sobel(candidate, cv2.CV_32F, 0, 1)
                    MinX_range_Candidate = abs(np.max(Xgradient_candidate) - np.min(Xgradient_candidate))
                    MinY_range_Candidate = abs(np.max(Ygradient_candidate) - np.min(Ygradient_candidate))
                    
                    if MinX_range_Candidate <= MinX_range and MinY_range_Candidate <= MinY_range:
                        MinX_range = MinX_range_Candidate
                        MinY_range = MinY_range_Candidate
                        selected_neighbor = candidate
            
            if selected_neighbor is not None:
                source = cv2.seamlessClone(selected_neighbor, source, ROI_Mask, (x, y), cv2.NORMAL_CLONE)
                break  
            radii = math.ceil(radii/2)
            if(radii<4): break
        
        cv2.imshow(winname, source) 

def RunGUI_BlmeshRemover_RunGUI(path):
    global source
    source = cv2.imread(path,1)
    dummy = source.copy()
    cv2.namedWindow(winname)
    cv2.setMouseCallback(winname, BlemishRemover)
    k=0
    while k!=27 :
        cv2.imshow(winname,source)
        k = cv2.waitKey(20) & 0xFF

        if k==101 or k==69:
            source= dummy.copy()
            cv2.imshow(winname, source) 

    cv2.destroyAllWindows()

if __name__ == "__main__":
    ImagePath = "blemish.png"
    RunGUI_BlmeshRemover_RunGUI(ImagePath)
