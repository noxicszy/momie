# -*- coding:utf-8 -*-
import cv2
import numpy as np
import os
import time
import pickle


class ImageSet:
    def __init__(self):
        self.N = 8
        self.dimension = self.N**2
        if not os.path.exists('baskets.pkl'):
            self.baskets = {}
        else:
            with open('baskets.pkl', 'rb') as pickle_file:
                self.baskets = pickle.load(pickle_file)

        if not os.path.exists('appids.pkl'):
            self.appids = set()
        else:
            with open('appids.pkl', 'rb') as pickle_file:
                self.appids = pickle.load(pickle_file)

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
        features = np.array([]).astype(np.uint8)
        for y in range(len(image)):
            for x in range(len(image[0])):
                features = np.hstack((features, image[y][x].astype(np.uint8)))
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
        
    def addapp(self, appid):
        self.appids.add(appid)

    def hasapp(self, appid):
        return appid in self.appids

    def sortResult(self, similars, target_features):
        result = []
        for filename, features in similars:
            distance = (np.sum((target_features-features)**2))**(0.5)
            result.append([distance, filename])
        result.sort()
        for i in range(len(result)):
            result[i] = result[i][1]
        return result 

    def getSimilar(self, image):
        """返回一个列表，元素是图片的url，优先度已经排序 """
        features = self.getFeatures(image)
        LSH = self.getLSH(features)
        if LSH in self.baskets:
            similars = self.baskets[LSH]
        else:
            return None
        result = self.sortResult(similars, features)
        return result
            
print 'loading imgs...'           
imageSet = ImageSet()


if __name__ == '__main__':
    targetname = 'test.jpg'
    targetimg = cv2.imread(targetname, cv2.IMREAD_COLOR)
    similars = imageSet.getSimilar(targetimg)
    print similars