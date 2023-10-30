#!/usr/bin/env python
# coding: utf-8

# In[15]:


# Project Title: Ride-Share Algorithm Tester 
#
# Author: Richard Kershner
#         with assistance from: ---
#         using code from: ---
#
# Completion Date: 2023_10-08
#
# Ride_Requests()
#
# Description: 
#        - Generates addresses and time for pickup and dropoff of a request
#
# Precondition:
#        - called with number of epochs, how many tests to do.
#        - Called with number of requests in a group in an epoch
#
# Postcondition:
#       - Provides next group of requests in an epoch
#
# Implementation:
#         1.  Generate values
#         2.  Supply values when called           
#
# include files go here (lines included below just an example)
#        from Mapper import Mapper << included in Main >>
#        import random

import random

class Ride_Requests():
    def __init__(self, epochSize, groupSize, mapper, rType = "normal"):
        
        # format is [[addressPickUp, addressDropOff, timeRequested], ...]
        self.epochList = []
        
        if rType == "spoke-in":
            self.generateRandomEpoch_SpokeIn(epochSize, groupSize, mapper)
        elif rType == "spoke-out":
            self.generateRandomEpoch_SpokeOut(epochSize, groupSize, mapper)
        else:
            self.generateRandomEpoch(epochSize, groupSize, mapper)
        
        self.pnt_epoch = 0
        
    
    def generateRandomEpoch(self, epochSize, groupSize, mapper):
        pnt = 0
        for epoch in range(epochSize):
            self.epochList.append([])
            for g in range(groupSize):
                group = mapper.getRandomAddresses()
                requestedTime = random.randint(0, 2) * 6 # generated 0 to n or n(6)*5=30 minutes in 5 minute intervals
                group.append(requestedTime)
                self.epochList[pnt].append(group)
            pnt +=1
            
    # Author: Richard Kershner
    #         with assistance from: ---
    # Description:
    #      Same as generateRandomEpoch but all rides end at one point.  Like going to a main bus terminal
    # Completion Date: 2023_10-02
    def generateRandomEpoch_SpokeIn(self, epochSize, groupSize, mapper):
        
        for epoch in range(epochSize):
            self.epochList.append([])
            
            address1 = mapper.getRandomAddress()
            
            for g in range(groupSize):
                
                requestedTime = random.randint(0, 7) * 5 # generated 0 to 30 minutes in 5 minute intervals
                request = [mapper.getRandomAddress_seeded(address1), address1, requestedTime]
                
                self.epochList[-1].append(request)
            
    # Author: Richard Kershner
    #         with assistance from: ---
    # Description:
    #      Same as generateRandomEpoch but all rides start at one point.  bus terminal or school pickup
    # Completion Date: 2023_10-02
    def generateRandomEpoch_SpokeOut(self, epochSize, groupSize, mapper):
        
        for epoch in range(epochSize):
            self.epochList.append([])
            
            address2 = mapper.getRandomAddress()
            
            for g in range(groupSize):
                
                requestedTime = random.randint(0, 7) * 5 # generated 0 to 30 minutes in 5 minute intervals
                request = [address2, mapper.getRandomAddress_seeded(address2), requestedTime]
                
                self.epochList[-1].append(request)
    
    def getNextRequestGroup(self):
        # --- Test for end of list
        if self.pnt_epoch >= len(self.epochList):
            return None
        
        # return group and increment pointer to next group
        group = self.epochList[self.pnt_epoch]
        self.pnt_epoch += 1
        return group

    
# =============================== testing ==========
# ================ test imports =======================
import os
import sys
programPath = os.path.dirname(os.path.abspath("tempTest.ipynb"))
sys.path.append(programPath + "\\modules")
programPath = os.path.dirname(os.path.abspath("tempTest.py"))
sys.path.append(programPath + "\\modules")
from Mapper import Mapper

if __name__ == "__main__":
    mapper = Mapper(programPath)

    addr = mapper.getRandomAddresses()

    print(addr)
    print(mapper.getRandomAddresses())
    print(" ------ ")
    
    rideRequests = Ride_Requests(3, 4, mapper)
    
    for group in rideRequests.epochList:
        print()
        for request in group:
            print(request)
    print("--------")       
    group = rideRequests.getNextRequestGroup()
    for request in group:
        print(request)
    
    # test get next group
    rideRequests = Ride_Requests(3, 4, mapper)
    while True:
        requestGroup = rideRequests.getNextRequestGroup()
        if requestGroup == None: 
            print("found end group")
            break
            
    print()
    rideRequests = Ride_Requests(3, 4, mapper, rType = "spoke-in")
    while True:
        requestGroup = rideRequests.getNextRequestGroup()
        print("---- spoke in group ---")
        if requestGroup == None: 
            print("found end group")
            break
        else:
            for g in requestGroup:
                print("   ", g)
                
    print()
    rideRequests = Ride_Requests(3, 4, mapper, rType = "spoke-out")
    while True:
        requestGroup = rideRequests.getNextRequestGroup()
        print("---- spoke out group ---")
        if requestGroup == None: 
            print("found end group")
            break
        else:
            for g in requestGroup:
                print("   ", g)
            
    


# In[ ]:




