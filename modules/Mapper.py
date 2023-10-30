#!/usr/bin/env python
# coding: utf-8

# In[17]:


import random

class Mapper():
    
    def __init__(self, filePath):
        
        # dictionary is in the form {"address1":{"address2":routeInfo},"address3": ....}
        #      routInfo is based on googe maps, {"distance":float, "time":float, 
        #                "Xs":[float, float, ...], "Ys":[float, float, float...].... }
        self.mapper = dict()
        
        # load dictionary from preset files.
        self.loadMapperFromFile(filePath)
    
    # Author(s):  Richard Kershner
    # Description:
    #     A file was created with a list of addresses connect to other addresses
    #        This is the short list downlaoded from Google Maps
    #        Note, information altered as this is NOT actual data, Google licensing prohibits
    def loadMapperFromFile(self, filePath):
        fileName = filePath + "\\mapperDataFromGoogle.txt"
        with open(fileName, 'r') as file:
            for line in file:
                rowArray = line.split(";;")
                if (rowArray[0] != "") and (rowArray[1] != ""):
                    if rowArray[0] not in self.mapper:
                        self.mapper[rowArray[0]] = dict()
                    self.mapper[rowArray[0]][rowArray[1]] = dict() # add second addr.
                    self.mapper[rowArray[0]][rowArray[1]]['time'] = int(rowArray[2])
                    self.mapper[rowArray[0]][rowArray[1]]['distance'] = float(rowArray[3])
                    # float_array = [float(x) for x in string_array]

                    self.mapper[rowArray[0]][rowArray[1]]['Xs'] = [float(x) for x in rowArray[4].split(",")]
                    self.mapper[rowArray[0]][rowArray[1]]['Ys'] = [float(x) for x in rowArray[5].split(",")]
            
            # nothing to return

    # Author(s):  Richard Kershner
    # Description:
    #     returns [X], [Y] for the address for for mapping purposes
    def getAddressXY(self, address):
        key = list(self.mapper[address].keys())[0]
        
        info = self.mapper[address][key]
        Xs = [info['Xs'][0]]
        Ys = [info['Ys'][0]]
        
        return Xs, Ys
        
    
    # Author(s):  Richard Kershner
    # Description:
    #     Get two different random addresses that are in the loaded dictionary
    #     Used in generating random requests and request groups for testing
    def getRandomAddresses(self):
        address1 = self.getRandomAddress()
        address2 = self.getRandomAddress_seeded(address1)
        
        return [address1, address2]
    
    # Author(s): Richard Kershner
    # Description:
    #     Get a random single address as opposed to two.  Used for spoke seeding
    def getRandomAddress(self):
        return random.choice(list(self.mapper.keys()))
    
    # Author(s): Richard Kershner
    # Description:
    #     Get a random single address under a seed address as opposed to two.  Used for spoke seeding  
    def getRandomAddress_seeded(self, addressSeed):
        return random.choice(list(self.mapper[addressSeed].keys()))
    
    # Author(s):  Richard Kershner
    # Description:
    #     retrieve Google maps altered data from dictionary
    #       returns as a dictionary object
    #       {'time':float, "distance":float, "Xs":[], "Ys":[], ....}
    #        Xs and Ys are steps in the driving map which can be plotted overlay on a map
    def getRouteInfo(self, address1, address2, rev = False):
        info = self.mapper[address1][address2]
        return info

# ================== inline testing
import os
import sys
programPath = os.path.dirname(os.path.abspath("tempTest.ipynb"))
sys.path.append(programPath + "\\modules")
programPath = os.path.dirname(os.path.abspath("tempTest.py"))
sys.path.append(programPath + "\\modules")

if __name__ == "__main__":
    mapper = Mapper(programPath)
    for x in range(5):
        print()
        mapper = Mapper(programPath)

        addr = mapper.getRandomAddresses()

        print(addr)
        print(mapper.getRouteInfo(addr[0], addr[1]))
    print()
    print("spoke out")
    for y in range(2):
        addr = mapper.getRandomAddress()
        print(addr)
        for x in range(3):
            address2 = mapper.getRandomAddress_seeded(addr)
            print("  ", address2)
        print()
        print("single address")
        addr = mapper.getRandomAddress()
        print(addr)
        print(mapper.getAddressXY(addr))


# In[ ]:





# In[ ]:




