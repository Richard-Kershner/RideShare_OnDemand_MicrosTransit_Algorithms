#!/usr/bin/env python
# coding: utf-8

# In[7]:


class Route():
    def __init__(self, mapper, algoName, groupNumber):
        
        self.algorithmUsed = algoName
        self.mapper = mapper
        self.groupNumber = groupNumber
        
        # stops, each row, mixed list, [ID, time, minTime, maxTime, address]
        # [[0, 45, 45, 55, '1819 Sunlight Dr'],....
        self.stops = [] #+ Route_Stop[] stops
    
    def addStop(self, stop, index):
        # stop --> [0, 45, 45, 55, '1819 Sunlight Dr']
        
        # base case, empty route
        if len(self.stops) == 0:
            #print("        ---- route base case empty, adding ", index)
            self.stops.append(stop)
            return 0 # valid fit.  No pushing
        
        self.stops.insert(index, stop)
        self.pushBackSched(index)
        weight = 0
        
        if index == 0:
            weight = self.pushForwardSched(index)
        else:
            weight = self.pushForwardSched(index-1)
        
        return weight
    
    # Author:  Richard Kershner
    # Description: If exists, delete request which is stops referenced by ID
    # Date initiated/completed: 2023_10-02 / 2023_10_02
    def del_request(self, ID):
        # must remove ID in reverse as stops is changed
        for s in range(len(self.stops) - 1, -1, -1):
            if self.stops[s][0] == ID:
                del(self.stops[s])
                       
        
    def get_stops(self):
        return self.stops
    
    def pushBackSched(self, pointer):
        
        # going from pointer back.. move rides back as much as possilbe
        #   instead this should be zero forward
        #      by doing all rides pushed back as much as possible it would
        #      remove gaps if future testings include dropping rides.
        # Must include who is on the bus and not mess up future pickup
        #   For instance, if a pickup window is 0 to 10
        #     and current time is 10
        #     and drive to next pickup is 10
        #     and their pickup is set to minimal time wihch is 20
        #     then moving ride back would have the passanger 1
        #        sitting on the bus for 10 minutes waiting for next pickup
            
        return
        
        for slot in range(pointer, 0, -1):
            address1 = self.stops[slot][4] 
            address2 = self.stops[slot-1][4]
            driveTime = self.mapper.getRouteInfo(address1, address2)['time']
            
            # done adjusting, fits. 
            if driveTime < (self.stops[slot][1] - self.stops[slot-1][1]):
                return
            
            if driveTime <= (self.stops[slot][1] - self.stops[slot - 1][2]):
                self.stops[slot - 1][1] = self.stops[slot][1] - driveTime
            
            else:
                diffTime = (self.stops[slot][1] - driveTime) - self.stops[slot-1][2]
                return
            
        # no changes, so fits.
        return
    
    def pushForwardSched(self, pointer):
        
        # Case 1, end of route changes, this part fits
        if pointer + 1 == len(self.stops):
            return 0
        
        address1 = self.stops[pointer][4]
        address2 = self.stops[pointer +1][4]
        driveTime = 0
        if address1 != address2:
            driveTime = self.mapper.getRouteInfo(address1, address2)['time']
            
        # Case, fits and doesn't need any changes
        if self.stops[pointer + 1][1] > (self.stops[pointer][1] + driveTime):
            return 0
        
        # removed ---- if previous one fit on pointer - 1, kicked out
        #    by removing this, auto corrects other errors.
        # Case 2, don't need to push forward the next one, it already fits 
        #if (self.stops[pointer][1] + driveTime) < self.stops[pointer + 1][1]:
        #    return 0
        
        # Case 3, doesn't fit. time + travel time greater then max
        if self.stops[pointer][1] + driveTime > self.stops[pointer + 1][3]:
            # Pushes ride anyway
            #    In future exploration, might test if one vehicle is down
            #      and rides forced onto another vehicle.  
            #          The weight is then totol pushed back negative time
            
            # !!!!!!! note, see case 4.... need to make sure NOT before previous ride
            
            self.stops[pointer + 1][1] = self.stops[pointer][1] + driveTime
            
            weight = self.stops[pointer + 1][3] - (self.stops[pointer][1] + driveTime)
            w2 = self.pushForwardSched(pointer + 1)
            
            # if next pushback causes more crashing, added to negative weight
            if w2 < 0:
                weight =+ w2
            return weight
        # Case 4, might fit.
        else:
            self.stops[pointer + 1][1] = self.stops[pointer][1] + driveTime
            # !!!!!!! note, see case 3.... need to make sure NOT after next ride
            return self.pushForwardSched(pointer + 1)
            
        return weight
    
    def testRouteValid(self):
        # test for dead space... the larger the dead space....
        # test for over booking... the more overbooked......
        routeValidRatings = {"deadTime":0.0, "behindStops":0.0}
        
        # --- process who is on board the vehicle before computing issues.
        passengers = []
        
        for i in range(len(self.stops)-2): # drop off passanger if on board
            if self.stops[i][0] in passengers:
                passengers = list(filter(lambda p: p!= self.stops[i][0], passengers))
            else:# self.stops[i][0] not in onBoard:
                passengers.append(self.stops[0])
                
            # this address and next...  
            address1 = self.stops[i][4]
            address2 = self.stops[i+1][4]

            # --- Compute and add time to issues
            if address1 != address2:

                # drive between stops, drive time from stop and nextstop
                driveTime = self.mapper.getRouteInfo(address1, address2)["time"]
                actualStepTime = self.stops[i][1] + driveTime

                # difference in actuat step time and next stop
                #    If delta time > 0, there is a gap between stops and actual step time
                #       This is only calcualted if passangers on board
                #    If delta < 0, this means the drive is running behind
                deltaTime = self.stops[i+1][1] - actualStepTime 

                if deltaTime < 0: # running behind
                    # add amount as a possitive
                    routeValidRatings["behindStops"] += (-1 * deltaTime)

                elif (deltaTime > 0) and (len(passengers) > 0): # passengers are sitting on vehicle waiting
                    routeValidRatings["deadTime"] += deltaTime
                
        return routeValidRatings
    
# =================== temp Test ====================
import os
import sys
programPath = os.path.dirname(os.path.abspath("tempTest.ipynb"))
sys.path.append(programPath + "\\modules")
programPath = os.path.dirname(os.path.abspath("tempTest.py"))
sys.path.append(programPath + "\\modules")
from Mapper import Mapper

def printRoute(route):
    print("route")
    for i in range(len(route.stops)):
        driveTime = 0
        if i != 0 and (route.stops[i-1][4] != route.stops[i][4]):
            driveTime = mapper.getRouteInfo(route.stops[i-1][4], route.stops[i][4])['time']
        print("    ", route.stops[i], "  ", driveTime)

if __name__ == "__main__":
    mapper = Mapper(programPath)
    
    # create route
    route = Route(mapper, 2, 3)
    
    # create test list of requests
    requests = [['879 Neon Forest Circle', '1819 Sunlight Dr', 5]]
    requests.append(['2114 Lincoln St', '1715 Iron Horse Dr', 10])
    requests.append(['1819 Sunlight Dr', '879 Neon Forest Circle', 15])
    
    
    # stops format [[ID, time, minTime, maxTime, address], ... ]       
    #    stop --> [0, 45, 45, 55, '1819 Sunlight Dr']
    
    print("-- adding stops, not testing pushing --")
    # add stops in.  
    for i in range(len(requests)):
        # addStops(stop, index)  if empty returns 0.  negative if push forward and back. Possitive if down time on ride
        print("   request: ", i, "  ", requests[i])
        stop1 = [i, requests[i][2], requests[i][2], requests[i][2] + 10, requests[i][0]]
        stop2 = [i, requests[i][2], requests[i][2], requests[i][2] + 45, requests[i][1]]
        print("        stop2: ", stop2)
        print("        stop1: ", stop1)
        
        # always add stop2, drop-off first so index pushes back correctly
        weight2 = route.addStop(stop2, i)
        weight1= route.addStop(stop1, i)
        print("        weights 1 & 2 = ", weight1, " & ", weight2)
        
    print("requests")
    for i in range(len(requests)):
        print("    ", i, "  ", requests[i])
    printRoute(route)
    print()
    
    print("# ----------------------------")
    
    route = Route(mapper, 2, 3)
    
    print(" -- tests base case I, nothing to push  ")
    route.stops = [[1, 5, 0, 10, '879 Neon Forest Circle']] 
    route.stops.append([1, 5, 5, 15, '1819 Sunlight Dr'])
    print(0, " PB ", route.pushBackSched(0))
    print(1, " PF ", route.pushForwardSched(1))
    printRoute(route)
    print()
    
    print(" -- tests base case II, fits  ")
    route.stops = [[1, 0, 0, 10, '879 Neon Forest Circle']] 
    route.stops.append([1, 25, 25, 35, '1819 Sunlight Dr'])
    print(1, " PB ", route.pushBackSched(1))
    print(0, " PF ", route.pushForwardSched(0))
    printRoute(route)
    print()
    
    print(" -- tests push back 1  ")
    route.stops = [[1, 5, 0, 10, '879 Neon Forest Circle']] 
    route.stops.append([1, 15, 5, 15, '1819 Sunlight Dr'])
    printRoute(route)
    print(1, " PB ", route.pushBackSched(1))
    printRoute(route)
    print()
    
    print(" -- tests push forward 1  ")
    route.stops = [[1, 5, 0, 10, '879 Neon Forest Circle']] 
    route.stops.append([1, 15, 5, 25, '1819 Sunlight Dr'])
    printRoute(route)
    print(0, " PF ", route.pushForwardSched(0))
    printRoute(route)
    print()
    
    print(" -- tests push back 3  ")
    route.stops = [[1, 31, 0, 10, '879 Neon Forest Circle']] 
    route.stops.append([1, 33, 5, 33, '1819 Sunlight Dr'])
    route.stops.append([2, 35, 30, 45, '1715 Iron Horse Dr'])
    route.stops.append([3, 45, 45, 60, '2114 Lincoln St'])
    printRoute(route)
    print(3, " PB ", route.pushBackSched(3))
    printRoute(route)
    print()
    
    print(" -- tests push forward 3  ")
    route.stops = [[1, 31, 0, 10, '879 Neon Forest Circle']] 
    route.stops.append([1, 33, 5, 60, '1819 Sunlight Dr'])
    route.stops.append([2, 35, 30, 75, '1715 Iron Horse Dr'])
    route.stops.append([3, 45, 45, 80, '2114 Lincoln St'])
    printRoute(route)
    print(0, " PB ", route.pushForwardSched(0))
    printRoute(route)
    print()
    
    print(" -- tests push back 1  - Fail")
    route.stops = [[1, 5, 0, 10, '879 Neon Forest Circle']] 
    route.stops.append([1, 8, 5, 15, '1819 Sunlight Dr'])
    printRoute(route)
    print(1, " PB ", route.pushBackSched(1))
    printRoute(route)
    print()
    
    print(" -- tests push forward 1 - Fail  ")
    route.stops = [[1, 5, 0, 10, '879 Neon Forest Circle']] 
    route.stops.append([1, 8, 5, 10, '1819 Sunlight Dr'])
    printRoute(route)
    print(0, " PF ", route.pushForwardSched(0))
    printRoute(route)
    print()
    print("validation")
    print(route.testRouteValid())

    route.stops.append([2, 5, 0, 10, '879 Neon Forest Circle'])
    route.stops.append([2, 8, 5, 15, '1819 Sunlight Dr'])
    print()
    print(" get stops ")
    print(route.get_stops())
    
    print()
    ID = 1
    print("delete ID = ", ID)
    route.del_request(ID)
    print(route.get_stops())
    

    

    


# In[ ]:




