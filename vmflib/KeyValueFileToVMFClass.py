import re
from collections import OrderedDict
import json
from vmf import VmfClass
from math import cos, sin, radians


reString = re.compile("(\s+)?([A-z0-9\"]+)\s+?([A-z0-9\"].+)")

reSideString = re.compile("\(([0-9\-e.]+) ([0-9\-e.]+) ([0-9\-e.]+)\) \(([0-9\-e.]+) ([0-9\-e.]+) ([0-9.\-]+)\) \(([0-9\-e.]+) ([0-9\-e.]+) ([0-9.\-]+)\)")

def rotationZ(x, y, rotationAngle):
    rotationAngle = radians(rotationAngle)
    x_ = x * cos(rotationAngle) - y * sin(rotationAngle)
    y_ = x * sin(rotationAngle) + y * cos(rotationAngle)
    return x_, y_

def cleanUpComments(str_):
    str_ = str_.replace("'", "\"")
    if "//" not in str_:
        return str_
    i = 0
    quoteSplitStr = str_.split("\"")
    #print(quoteSplitStr)
    while (i < len(quoteSplitStr)):
        if "//" in quoteSplitStr[i]:
            quoteSplitStr[i] = quoteSplitStr[i].split("//")[0]
            return "\"".join([*quoteSplitStr[0:i], quoteSplitStr[i]])
        i += 2
    return str_

def _getKeyValue(buf):
        kv = reString.match(buf)
        if kv:
            return [kv.group(2).split("\"")[1] if "\"" in kv.group(2) else kv.group(2) ,
                kv.group(3).split("\"")[1] if "\"" in kv.group(3) else kv.group(3)]

class KeyValueFileToVMFClass(VmfClass):

    def __init__(
        self, 
        filename, 
        name = "importedRootElem", 
        translation = None, 
        rotationAngle = None
        ):
        self.vmf_class_name = name
        VmfClass.__init__(self)
        self.leveledDic_ = {}
        with open(filename, "r") as f:
            currentLevel_ = 0
            self.currentItemName = ""
            self.dic = VmfClass()
            self.currentDic = self
            self.parentDic = {}
            for buffer_ in f.read().strip().split("}"):
                for buffer__ in buffer_.strip().split("{"):
                    for tokenOrData in buffer__.strip().split("\n"):
                        tokenOrData = cleanUpComments(tokenOrData)
                        if tokenOrData:
                            kv = _getKeyValue(tokenOrData)
                            if kv == None:
                                currentDic_ = VmfClass()
                                currentDic_.vmf_class_name = tokenOrData.strip()
                                self.parentDic[currentLevel_] = self.currentDic
                                self.currentDic.children.append(currentDic_)
                                self.currentDic = currentDic_
                            else:

                                self.currentDic.properties[kv[0]] = kv[1]
                    currentLevel_ += 1
                currentLevel_ -= 2
                if currentLevel_ >= 0:
                    self.currentDic = self.parentDic[currentLevel_]

        if translation or rotationAngle != None:
            #print("translation x%.2f y%.2f z%.2f r%2.f" % (translation[0], translation[1], translation[2], rotationAngle))
            for child in self.children:
                if child.vmf_class_name in ["world", "entity"]:
                    self.recursTranslate(child, translation, rotationAngle)
                       
                            
                                   
                                    # print(solidChild.properties["plane"])
                                    # exit(0)
            #self.recursRead(buffer_)

    def recursTranslate(self, elem, translation, rotationAngle):
        translationX, translationY, translationZ = translation
        if "origin" in elem.properties:
            oX, oY, oZ = elem.properties["origin"].split(" ")[:3]
            oX, oY, oZ = float(oX), float(oY), float(oZ)

            if rotationAngle:
                oX, oY = rotationZ(oX, oY, rotationAngle)
            elem.properties["origin"] = "{0} {1} {2}".format(
                oX + translationX,
                oY + translationY,
                oZ + translationZ)
        if "angles" in elem.properties:
            aX, aY, aZ = elem.properties["angles"].split(" ")[:3]
            aX, aY, aZ = float(aX), float(aY), float(aZ)

            if rotationAngle:
                #oX, oY = rotationZ(oX, oY, rotationAngle)
                elem.properties["angles"] = "{0} {1} {2}".format(
                    aX,
                    aY + rotationAngle,
                    aZ)
        for grandChild in elem.children:
            if grandChild.vmf_class_name == "entity":
                recursTranslate(grandChild, translationX, translationY)
            if grandChild.vmf_class_name == "solid":
                for solidChild in grandChild.children:
                    if solidChild.vmf_class_name == "side":
                        #print(solidChild.properties["plane"])
                        a = reSideString.match(solidChild.properties["plane"])
                        if a == None:
                            #print(solidChild.properties["plane"])
                            exit(0)
                        Ax, Ay, Az = float(a.group(1)), float(a.group(2)), float(a.group(3))
                        Bx, By, Bz = float(a.group(4)), float(a.group(5)), float(a.group(6))
                        Cx, Cy, Cz = float(a.group(7)), float(a.group(8)), float(a.group(9))
                        if rotationAngle:
                            Ax, Ay = rotationZ(Ax, Ay, rotationAngle)
                            Bx, By = rotationZ(Bx, By, rotationAngle)
                            Cx, Cy = rotationZ(Cx, Cy, rotationAngle)

                        solidChild.properties["plane"] = "({0} {1} {2}) ({3} {4} {5}) ({6} {7} {8})".format(
                        repr(Ax + translationX), 
                        repr(Ay + translationY),
                        repr(Az + translationZ), 

                        repr(Bx + translationX), 
                        repr(By + translationY),
                        repr(Bz + translationZ), 
                        
                        repr(Cx + translationX), 
                        repr(Cy + translationY),
                        repr(Cz + translationZ), 
                    )