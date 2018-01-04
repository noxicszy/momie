import cv2
import numpy as np
import os
import time


class ImageSet:
    def __init__(self):
        self.baskets = {}
        self.N = 8
        self.dimension = self.N**2

    def getHist(self, image):
        BGR = np.zeros(3)
        for y in range(len(image)):
            for x in range(len(image[0])):
                for color in range(3):
                    BGR[color] += image[y][x][color]
        BGR /= np.sum(BGR)
        return BGR

    def getFeatures(self, image):
        image = cv2.resize(image, (self.N, self.N))
        features = np.array([])
        for y in range(len(image)):
            for x in range(len(image[0])):
                features = np.hstack((features, image[y][x]))
        return features
    
    def quantize(self, features):
        p = np.array([])
        for i in range(self.dimension):
            hist = features[i*3:i*3+3]
            MAX = max(hist)
            MIN = min(hist)
            for i in range(3):
                if hist[i] == MAX:
                    hist[i] = 0
                elif hist[i] == MIN:
                    hist[i] = 2
                else:
                    hist[i] = 1
            p = np.hstack((p, hist))
        return p

    def getLSH(self, features):
        p = self.quantize(features)        
        v = [0]*(self.dimension*6)
        for i in range(self.dimension*3):
            for j in range(i*2, i*2+int(p[i])):
                v[j] = 1
        
        # make projection
        #I = [1, 2, 4, 5, 16, 20]
        I = [i for i in range(self.dimension*6)]
        projection = []
        for i in I:
            projection.append(v[i])
        
        # transform binary list to decimal        
        n = 1
        sum = 0
        for i in range(len(projection)):
            sum += projection[i]*n
            n *= 2
        return sum
        
        
    def add(self, filename, image):
        features = self.getFeatures(image)
        LSH = self.getLSH(features)
        if LSH in self.baskets:
            self.baskets[LSH].append([filename, features])
        else:
            self.baskets[LSH] = [[filename, features]]
        return LSH
        
    def getNN(self, similars, target_features):
        result = []
        for filename, features in similars:
            distance = (np.sum((target_features-features)**2))**(0.5)
            result.append([distance, filename])
        result.sort()
        for i in range(len(result)):
            result[i] = result[i][1]
        return result 

    def getSimilar(self, image):
        features = self.getFeatures(image)
        LSH = self.getLSH(features)
        if LSH in self.baskets:
            similars = self.baskets[LSH]
        else:
            return None
        result = self.getNN(similars, features)
        return result
            
            
            
if __name__ == '__main__':
    imageSet = ImageSet()
    dirpath = 'dataset/'
    filelist = os.listdir(dirpath)
    targetfile = '12.jpg'


    start_time = time.time()
    for filename in filelist:
        image = cv2.imread(os.path.join(dirpath, filename), cv2.IMREAD_COLOR)
        imageSet.add(filename, image)

    start_time = time.time()
    targetimage = cv2.imread(targetfile, cv2.IMREAD_COLOR)
    similars = imageSet.getSimilar(targetimage)
    print similars
    print "LSH costs {}s".format(time.time()-start_time) 
    # method using LSH ends
    

