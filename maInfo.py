import math
import ntpath
import re
from sys import argv
import json
from os import listdir, walk
from os.path import isfile, isdir, join, splitext

class Ma(object):
    def __init__(self, path):
        self.path = path

    def isMaya(self):
        filesMaya = []
        filesAll = []

        if isdir(self.path):
            for root, dirs, files in walk(self.path):
                for item in files:
                    filesAll.append(join(root, item))
            for item in filesAll:
                if item.endswith('.ma'):
                    filesMaya.append(item)
            return list(filesMaya)

        elif isfile(self.path):
            if self.path.endswith('.ma'):
                return self.path

    def openFile(self, mayaFile):
        with open(mayaFile, 'r') as openFile:
            return openFile.read()

    def writeJson(self):
        data = {}
        for mayaFile in self.isMaya():
            item = self.openFile(mayaFile)

            data["version"] = self.__reVersionMaya(item)
            data["faces"] = self.polyCount(item)
            data["renderer"] = self.__reActiveRenderer(item)
            data["renderer_version"] = self.__reRendererVer(item)
            #data["plugins_used"] = None
            data["objects_number"] = len(self.__reDagObjects(item))
            data["external_assets"] = self.__reFilePaths(item)
            data["materials"] = self.__reMaterials(item)

            with open(splitext(mayaFile)[0] + ".json", "w") as outFile:
                json.dump(data, outFile, indent=4)

    def info(self):
        for mayaFile in self.isMaya():
            print("\n",mayaFile)
            item = self.openFile(mayaFile)
            self.__reModifiedLast(item)
            self.__reVersionMaya(item)
            print(self.__reActiveRenderer(item))
            print(self.__reRendererVer(item))
            print(self.__reFilePaths(item))
            self.__reMaterials(item)
            self.__reDagObjects(item)
            #self.__reFaces(item)
            self.__rePolygons(item)
            self.polyCount(item)
            self.quads(item)
            self.tris(item)
            self.ngons(item)
            self.polysPercentage(item)

    def __regexSearch(self, mayaFile, regex):
        return re.search(regex, mayaFile).group(1)

    def __regexFindAll(self, mayaFile, regex):
        return [i for i in re.findall(regex, mayaFile)]

    def __reModifiedLast(self, mayaFile):
        regex = re.compile(r'\/\/Last modified: (.*?)$', re.MULTILINE | re.DOTALL)
        return self.__regexSearch(mayaFile,regex)

    def __reVersionMaya(self, mayaFile):
        regex = re.compile(r'fileInfo "product" "\w* (\d*)";')
        return self.__regexSearch(mayaFile,regex)

    def __reActiveRenderer(self, mayaFile):
        regex = re.compile(r'select.*:defaultRenderGlobals;\n\tsetAttr.* "(\w*)";')
        return self.__regexSearch(mayaFile,regex)

    def __reRendererVer(self, mayaFile):
        regex =  re.compile(r'setAttr ".version" -type "string" "(.*?)";')
        return self.__regexSearch(mayaFile,regex)

    def __reFilePaths(self, mayaFile):
        regex = re.compile(r'setAttr ".ftn" .* "(.*)";')
        return self.__regexFindAll(mayaFile, regex)

    def __reDagObjects(self, mayaFile):
        regex = re.compile(r'createNode transform -n "(.*)";')
        return self.__regexFindAll(mayaFile, regex)

    def __reMaterials(self, mayaFile):
        regex = re.compile(r'createNode (?:lambert|blinn|phong) -n "(.*)";')
        return self.__regexFindAll(mayaFile, regex)

    def __reFaces(self, mayaFile):
        regex = re.compile(r'(?:createNode transform -n )(".*?").*?(?:setAttr -s )(\d*)(?: -ch \d* ).*?(?:-type "polyFaces" ).*?f (\d).*?$', re.MULTILINE | re.DOTALL)
        return self.__regexFindAll(mayaFile, regex)

    def __rePolygons(self, mayaFile):
        regex = re.compile(r'\tf (\d)', re.MULTILINE | re.DOTALL) 
        a = self.__regexFindAll(mayaFile, regex)
        return [int(i) for i in a]

    def polyCount(self, mayaFile):
        faces = self.__rePolygons(mayaFile)
        polycount = len(faces)
        return polycount

    def quads(self, mayaFile):
        return self.__rePolygons(mayaFile).count(4)

    def tris (self, mayaFile):
        return self.__rePolygons(mayaFile).count(3)

    def ngons(self, mayaFile):
        p = self.__rePolygons(mayaFile)
        return sum(i > 4 for i in p)

    def polysPercentage(self, mayaFile):
        q = self.quads(mayaFile)
        pc = self.polyCount(mayaFile)
        rubbish = pc - q
        quadsPercent = math.trunc(round(q * 100.0 / pc))
        otherPercent = math.trunc(round((pc - q) * 100.0 / pc))
        return quadsPercent, otherPercent


ma = Ma(argv[1])
ma.isMaya()
ma.info()
ma.writeJson()

# if foo.ma History is not deleted then polycount might be slightly off