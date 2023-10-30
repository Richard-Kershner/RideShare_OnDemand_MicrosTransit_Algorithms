#!/usr/bin/env python
# coding: utf-8

# In[11]:


# Project Title: Ride-Share Algorithm Tester 
#
# Author: Richard Kershner
#         with assistance from: ---
#         using code from: ---
#
# Completion Date: 2023_10-08
#
# Algorithms()
#
# Description: 
#        - Holds the processes for creating different routing options. 
#        - 1.  Finds different pick-up and drop-off stop options.
#        - 2.a  Each test algorithm recieves existing route and different options.
#        - 2.b  Each test algorithm returns sorted list of "best" fits of options.
#        - 3.  Returned sorted lists are tested in sorted order for if they are valid.
#
# Precondition:
#        Route class submitted has list of stops with location (x, Y) and time of the stop
#        Request has a pick-up location(X,Y), drop-of location(X,Y) and a requested time
#        A mapper routine is supplied for looking up drive times between two locations
#        Restrictions for the options are hard coded into the class
#            A maximum and minimum time from the requested time the ride can be changed by
#            A maximum time from pick-up time, the drop-off time can be placed.
#
# Postcondition:
#        Provides ordered list of pick-up and drop-off stops for options
#        Provides a list of algorithms being tested and corresponding functions to call 
#        Current algorithms tested:
#            list get_sorted_Time():
#                Returns list of stops ordered by which rides are closest to requested time
#                If times are equal, the latter time is chosen     
#            list get_sorted_TravelTime():
#                Returns list of stops ordered by which one has shortest ride time for request
#                equal ride times goes to the one with pick_up time closest to request
#            get_sorted_Distance():
#                Returns list of stops ordered by which overall route change has lowest distance traveled
#                equal route distances goes to the one with pick_up time closest to request
#            list get_sorted_VectorMinimum():
#                Returns list based on other riders on the shared ride and the change in the vector
#                    vector math is based on grid and not pythagorean math.
#                    Total vector is (X2-X1) + (X3-X2) + ... + (Y2-Y1) + (Y3-Y2)+....
#                    This is different from get_sorted_Distance which is pulled from mapper
#                equal ride times goes to the one with pick_up time closest to request
#        NOTE: ON ALL ALGORITHMS:  drop-off has to be added to route before pick-up
#                if done in reverse, the insert index will NOT work
# Implementation:
#         1.  Options for pick-up stops is generated.
#             a.  Pick-up options must exist in the min/max window of time.
#             b.  Pick-up options are based on before/after fit of existing stops
#         2.  A new list is generated with each pick-up stop having drop-off stops options.
#             a.  Drop-off stops can NOT have down drive time where the passanger sits on the bus.
#             b.  Drop-off times must be within set limit of maximum ride time
#
# include files go here (lines included below just an example)
#        from Mapper import Mapper

class Algorithms():
    def __init__(self, mapper):
        
        # --- initialize variables ---
        self.mapper = mapper
        
        # --- Global Constants ---
        self.MIN_SCHEDULE_WINDOW = -45
        self.MAX_SCHEDULE_WINDOW = 45
        self.MAX_RIDE_TIME = 45
        
        # --- required from some algorithms
        self.requests = []
        
    # ===================================== INDIVIDUAL ALGORITHMS ====================================
    
    # ------------------------------------------------------------------- sorted time closest to request
    # Author(s):  Richard Kershner
    # Description:
    #        Sorts options based on closest time to requested time
    #        Multiple closest times goes to the time greater then
    #        Lastly, closest to lowest dropoff pnt insert
    def get_sorted_Time(self, routeStops, request):
        options = self.get_options(request[2], routeStops)
        
        # append T/F if option after and append delta time, difference between requeset and option
        for i in range(len(options)):
            greaterThen = request[2] > options[i][1]
            options[i].append(greaterThen)
            deltaTime = abs(options[i][1] - request[2])
            options[i].append(deltaTime)
            
        # sort (reverse order of importance) by 
        #     closest drop off pointer, closest index, then closest time
        options = sorted(options, key=lambda x:x[3]) 
        options = sorted(options, key=lambda x:x[4])
        options = sorted(options, key=lambda x:x[5])
        
        #print()
        #print("get_sorted_time... pick-up closest to request time, RAW sorted")
        #print(options)
        #print()
        
        # remove sorting columns
        options = [sublist[:4] for sublist in options]
        
        return options
    
    # ------------------------------------------------------------------- sorted travel time all passangers
    # Author(s):  Richard Kershner
    # Description:
    #        Sorts options based on over all travel time for all passangers minimized
    #        Multiple equal options sort on time closest to requested time
    def get_sorted_TravelTime(self, routeStops, request):
        options = self.get_options(request[2], routeStops)
        
        # for each index (dictionary), who is on the bus
        stopPassangers = dict()
        passangers = []
        for i in range(len(routeStops)):
            # pickup passanger if not onboard
            if routeStops[i][0] not in passangers:
                passangers.append(routeStops[i][0])
                stopPassangers[i] = passangers.copy()
            # dropoff passanger if already on board
            else:
                passangers = list(filter(lambda p: p!= routeStops[i][0], passangers))
            stopPassangers[i] = passangers.copy()
            
        for i in range(len(options)):
            deltaTime = 0
            # for pickup and dropoff
                # calcualte add time passanger count: A -> new stop & new stop -> B
                # calculate remove time for passanger count: A -> new stop -> B, time A -> B
                
            # no rides, no delta time
            if len(routeStops) != 0:
                
                # index can't be past length of stops, else weight is 0
                # pickup A is pnt.  pnt + 1 is B.   If pnt + 1 is passed endof stops, nothing
                if options[i][0] < (len(routeStops) - 1):
                    address1 = request[0]
                    addressA = routeStops[options[i][0]][4]
                    addressB = routeStops[options[i][0] + 1][4]
                    if address1 != addressA:
                        deltaTime =+ len(stopPassangers[options[i][0]]) * self.mapper.getRouteInfo(address1, addressA)['time']
                    if addressB != address1:   
                        deltaTime =+ len(stopPassangers[options[i][0]+1]) * self.mapper.getRouteInfo(addressB, address1)['time']
                    
        
                # If index is not at 0, (and not passed end), add adjustment before
                # drop of  is B.  pnt - 1 is A.  if at start, nothing there, so nothing
                pntB = options[i][2]
                pntA = pntB - 1
                if pntA >= 0 and (pntB < len(routeStops) ): 
                    address2 = request[1]
                    addressA = routeStops[pntA][4]
                    addressB = routeStops[pntB][4]
                    if addressA != address2:
                        deltaTime =+ len(stopPassangers[pntA]) * self.mapper.getRouteInfo(addressA, address2)['time']
                    if address2 != addressB:
                        deltaTime =+ len(stopPassangers[pntB]) * self.mapper.getRouteInfo(address2, addressB)['time']
            
            options[i].append(deltaTime)
            deltaTime = abs(options[i][1] - request[2])
            options[i].append(deltaTime)
                                                      
        # sort by reverse importance, lowest drop off index, deltaTime from request, ridersTime
        options = sorted(options, key=lambda x:x[2])
        options = sorted(options, key=lambda x:x[5])
        options = sorted(options, key=lambda x:x[4])
        
        #print()
        #print("160 - over all passanger ride time RAW")
        #print(options)
        #print()
        
        # remove sorting columns
        options = [sublist[:4] for sublist in options]
        return options
    

    # ------------------------------------------------------------------- sorted distance
    # Author(s):  Richard Kershner
    # Description:
    #        Sorts options based on over all travel distance minimized
    #        Multiple equal options sort on time closest to requested time
    def get_sorted_Distance(self, routeStops, request):
        options = self.get_options(request[2], routeStops)
        for i in range(len(options)):
            deltaDistance = 0
            address_PU = request[0]
            address_DO = request[1]
            
            # ----- calcualte change in distance driven before and after each insert (pick-up and drop-off) ----
            #           note, if insert is same number, drop-off before and pick-up after computes
            #                 as one distance, the distance between pick-up and drop-off
            # if ride exists before pick-up
            if options[i][0] != 0:
                # compute distance prior to pickup.  insert of 1 would push existing 1 forward, previous is i-1
                address_before_PU = routeStops[options[i][0]-1][4]
                if address_PU != address_before_PU:
                    deltaDistance =+self.mapper.getRouteInfo(address_PU, address_before_PU)['distance']
                
            # if ride exists after drop-off 
            if (options[i][2] + 1) < len(routeStops):
                # compute and add distance after drop-off. pushes existing i forward, so next ride is i
                address_after_DO = routeStops[options[i][2] + 1][4]
                if address_PU != address_after_DO:
                    deltaDistance =+ self.mapper.getRouteInfo(address_PU, address_after_DO)['distance']
                
            # if pickup and drop off pointers are the same, then next to each other
            #    This should show up as before + this + after drive distance
            #        Note before and after are computed above
            if options[i][0] == options[i][2]:
                # compute and add distance between pick-up and drop-off
                deltaDistance =+self.mapper.getRouteInfo(address_PU, address_DO)['distance']
                
                
            # if not same insert slot,meening they are next to each other, then rides exist between
            #    before + pickup + afterpickup .... + before drop off + after drop off
            #     above already calculates before+ and +after
            #     must subtract before pickup to after pickup and before drop off to after drop off
            #        This is replaced with the other distances
            else:
                # after pickup.  Must occur if rides between
                address_after_PU = routeStops[options[i][0]][4]
                address_before_DO = routeStops[options[i][0] - 1 ][4]
                
                # add distace after pickup.  Before pickup already handled above
                if address_PU != address_after_PU:
                    deltaDistance =+self.mapper.getRouteInfo(address_PU, address_after_PU)['distance']
                
                # add distance after dropoff.  After dropoff alerady handled above
                if address_before_DO != address_DO:
                    deltaDistance =+self.mapper.getRouteInfo(address_before_DO, address_DO)['distance']
                
                
                # subtract from before pickup to after pickup, if before exists
                if options[i][0] > 0:
                    address_before_PU = routeStops[options[i][0]-1][4]
                    if address_before_PU != address_after_PU:
                        deltaDistance =- self.mapper.getRouteInfo(address_before_PU, address_after_PU)['distance']
                    
                # subtract from after before dropoff to after dropoff, if after exists
                if options[i][0] + 1 < len(routeStops):
                    address_after_DO = routeStops[options[i][0]+1][4]
                    if address_after_DO != address_before_DO:
                        deltaDistance =- self.mapper.getRouteInfo(address_before_DO, address_after_DO)['distance']

            options[i].append(deltaDistance)
            deltaTime = abs(options[i][1] - request[2])
            options[i].append(deltaTime)
        
        # sort by reverse importance, lowest drop off index, deltaTime from request, distance
        options = sorted(options, key=lambda x:x[2])
        options = sorted(options, key=lambda x:x[5])
        options = sorted(options, key=lambda x:x[4])
        #print("250 - vehicle distance test raw, ", options)
        
        # remove sorting columns
        options = [sublist[:4] for sublist in options]
        
        return options
    
    # ------------------------------------------------------------------- sorted drive time
    # Author(s):  Richard Kershner
    # Description:
    #        Sorts options based on over all drive time minimized
    #        Multiple equal options sort on time closest to requested time
    def get_sorted_DriveTime(self, routeStops, request):
        options = self.get_options(request[2], routeStops)
        for i in range(len(options)):
            deltaTime = 0
            
            address_PU = request[0]
            address_DO = request[1]
            
            # ----- calcualte change in time driven before and after each insert (pick-up and drop-off) ----
            #           note, if insert is same number, drop-off before and pick-up after computes
            #                 as one distance, the distance between pick-up and drop-off
            
            # if ride exists before pick-up
            if options[i][0] != 0:
                # compute distance prior to pickup.  insert of 1 would push existing 1 forward, previous is i-1
                address_before_PU = routeStops[options[i][0]-1][4]
                if address_before_PU != address_PU:
                    deltaTime =+self.mapper.getRouteInfo(address_before_PU, address_PU)['time']
                
            # if ride exists after drop-off
            if options[i][2] < len(routeStops):
                # compute and add distance after drop-off. pushes existing i forward, so next ride is i
                address_after_DO = routeStops[options[i][2]][4]
                if address_DO != address_after_DO:
                    deltaTime =+self.mapper.getRouteInfo(address_DO, address_after_DO)['time']
                
            # if pu next to do include drive time
            if options[i][0] == options[i][2]:
                # compute and add distance between pick-up and drop-off
                if address_PU != address_DO:
                    deltaTime =+self.mapper.getRouteInfo(address_PU, address_DO)['time']
                
            # if not same insert slot,meening they are next to each other, then rides exist between
            #     (Pickup to after PU) + (before DO to Dropoff)
            #     Before pick and after dropp off already taken care of
            #     must subtract time from before to after PU and before to after DO
            else:
                # compute and add distance after pick-up and next ride in route
                address_after_PU = routeStops[options[i][0]][4]
                if address_PU != address_after_PU:
                    deltaTime =+ self.mapper.getRouteInfo(address_PU, address_after_PU)['time']
                # compute and add distance before drop-off and previous ride in route
                address_before_DO = routeStops[options[i][2] - 1 ][4]
                if address_before_DO != address_DO:
                    deltaTime =+ self.mapper.getRouteInfo(address_before_DO, address_DO)['time']
                
                # subtract time before/after PU as replaced by above
                if options[i][0] != 0:
                    address_before_PU = routeStops[options[i][0]-1][4]
                    if address_before_PU != address_after_PU:
                        deltaTime =- self.mapper.getRouteInfo(address_before_PU, address_after_PU)['time']
                
                # subtrack time before to after DO as replaced by above
                if (options[i][2] + 1) < len(routeStops):
                    address_after_PU = routeStops[options[i][2]+1][4]
                    if address_before_DO != address_after_DO:
                        deltaTime =- self.mapper.getRouteInfo(address_before_DO, address_after_DO)['time']

            options[i].append(deltaTime)
            deltaRequestTime = abs(options[i][1] - request[2])
            options[i].append(deltaRequestTime)
        
        # sort by reverse importance, lowest drop off index, deltaTime from request, distance
        options = sorted(options, key=lambda x:x[2])
        options = sorted(options, key=lambda x:x[5])
        options = sorted(options, key=lambda x:x[4])
        #print()
        #print("vehicle drive time test RAW sorted")
        #print(options)
        #print()
        
        # remove sorting columns
        options = [sublist[:4] for sublist in options]
        
        return options
    
    # ------------------------------------------------------------------- get_sorted_passangerXY_reqXY
    # Author(s):  Richard Kershner
    # Description:
    #        Sorts options based on vectors of passangers - vectors of request
    #            (requestX2 - passangerSumX2 - (requestX1 - passangerSumX1)
    #          + (requestY2 - passangerSumY2 - (requestY1 - passangerSumY1)
    #        Multiple equal options sort on time closest to requested time
    def get_sorted_passangerXY_reqXY(self, routeStops, request):
        
        # retrieve options available
        options = self.get_options(request[2], routeStops)
        
        # append difference in pick-up option vs request and default weight 0.0
        for i in range(len(options)):
            # abs(pick-up time - request time) delta from request to actual pick-up
            options[i].append(abs(request[2]-options[i][1]))
            
            # initilize weight as 0.0  options[i][5]
            options[i].append(0.0)
        
        # information for computing this rides and the difference between 
        #    the average of the people on the bus
        rMap = self.mapper.getRouteInfo(request[0], request[1])
        rX1 = rMap['Xs'][0]
        rY1 = rMap['Ys'][0]
        rX2 = rMap['Xs'][-1]
        rY2 = rMap ['Ys'][-1]
        
        # This is used to computer passanger averages
        #   for each passanger there is the Xs and Ys as with request X1 rX1, notation
        passangerDict = dict()
        for i in range(len(routeStops)):
            
            ID = routeStops[i][0]
            
            if ID not in passangerDict.keys():
                passangerDict[ID] = routeStops[i][4] # store address
            else:
                address_PU = passangerDict[ID] # get temp stored address
                address_DO = routeStops[i][4]
                pMap = self.mapper.getRouteInfo(address_PU, address_DO)
                
                # update from address marker to full information
                passangerDict[ID] = [pMap['Xs'][0], pMap['Ys'][0], pMap['Xs'][-1], pMap['Ys'][-1]]
        
        # build a list of who is on board at each stop
        #  note, i references which routeStop, while ID is the passanger number
        passangerList = dict()
        currentPass = []
        for i in range(len(routeStops)):
            passangerList[i] = currentPass.copy()
            ID = routeStops[i][0] 
            
            # add passanger if pick-up
            if  ID not in currentPass:
                currentPass.append(ID)
            # remove passanger if dropp-off                   
            else:
                currentPass = list(filter(lambda p: p!= ID, currentPass))
                                                          
        # now look at each option.  from start to end of pointes

        
        # for each optoin, reate a weight based on passangers avarages...
        #    this should be updated to be only the last stop for XYs 0, 1 !!!!!!!!!!!!!!!!
        for i in range(len(options)):
            
            # calculate for each option, for all the stops between pickup and dropoff
            # since pickup is before option[i][0], everyone on board during that pickup is affected
            # since dropoff is berfore option[i][2], eveyone on board during drop off is affected
            for j in range(options[i][0], options[i][2]):
                
                # proccess for each stop - create unique list of passangers for this option
                pList = []
                for p in passangerList[j]: # passanger List is who is on board for a stop
                    if p not in pList:
                        pList.append(p)
                        
                # initialize XYs
                XYs = [0.0, 0.0, 0.0, 0.0]
                
                # only process if there are passangers affected
                if len(pList) > 0:
                    
                    # add each x0, y0, x1, y1 for each passanger
                    for p in pList:
                        for k in range(4):
                            XYs[k] += passangerDict[p][k]
                    
                    # average the values
                    for m in range(4):
                        passangerDict[p][m] /= len(pList)
            
                if len(pList) > 0:
                    # add weight
                    #            (requestX2 - passangerSumX2) - (requestX1 - passangerSumX1)
                    #          + (requestY2 - passangerSumY2) - (requestY1 - passangerSumY1)
                    weight = (rX2 - XYs[2]) - (rX1 - XYs[0])
                    weight =+ (rY2 - XYs[3]) - (rY1 - XYs[1])
                    options[i][5] = abs(weight)
            
            # ----- END options loop
        
        # sort by reverse importance, lowest drop off index, deltaTime from request, weighted
        options = sorted(options, key=lambda x:x[2])
        options = sorted(options, key=lambda x:x[4])
        options = sorted(options, key=lambda x:x[5])
        #print()
        #print("vector RAW")
        #print(options)
        #print()
        
        # remove sorting columns
        options = [sublist[:4] for sublist in options]
        
        return options
    
    # ================================  END SEPERATE ALGORITHMS ===========================

    # ================================  GENERAL PROCESSING ===========================
        
        
    def get_algorithms(self):
        algorithmDict = dict()
        for method in dir(self):
            if method.startswith('get_sorted') is True:
                algorithmDict[method] = getattr(self, method)
        return algorithmDict
    
    def get_dropoffOptions(self, pickupOptions, stops):
        # get options. Route must be adjusted first and tested so as to not
        #    have dead drive times ???? What does that look like??????
        
        options = []
        
        # --- loop through pick-up options
        #       append pickup point, pickup time, dropoff pointer, dropoff time.
        #       One row for each different dropoff option
        for option in pickupOptions:
            pnt_PU = option[0]
            time_PU = option[1]
            
            # --- add option directly after pickup
            #     note, in scheduling route, drop off is scheduled first so this equals pickup
            options.append([pnt_PU, time_PU, pnt_PU, time_PU])
            
            # --- for each pickup option, loop through dropoff options
            #         Only if inside max ride time
            #    note: anything before is already tested, so always +1 on pointer
            for pnt_DO in range(pnt_PU + 1, len(stops)):
                if stops[pnt_DO][1] - time_PU <= self.MAX_RIDE_TIME:
                    newOption = [pnt_PU, time_PU, pnt_DO +1, stops[pnt_DO][1]]
                    # --- only add if not a duplicate
                    if newOption not in options:
                        options.append(newOption)
                
        return options
    
    # Author:  Richard Kershner
    # Description: Supplies final options list for list.
    # Requires:
    #    requestTime : from request of [adderss1, address2, time]
    #    stops: from route stops
    # Uses: get_pickupOpstions() and get_dropoffOptions()
    def get_options(self, requestTime, stops):
        
        if stops == [[]]:
            return [[0,requestTime, 0, requestTime + 1]]
        
        optionsPU = self.get_pickupOptions(requestTime, stops)
        
        return self.get_dropoffOptions(optionsPU, stops)
    
    
    # Author:  Richard Kershner
    # Description: Supplied with existing stops, returns pick_options
    #        1.  Each stop generates an option before and after
    #        2.  Requests only generated if time is with in minimum and maximium pick_up window
    # Requires:
    #    requestTime : from request of [adderss1, address2, time]
    # Produces:
    #    [[int pointer,int time]...] different valid places to insert pick-up
    def get_pickupOptions(self, requestTime, stops):

        puOptions = [] # [[int pointer,int time], ...]
        
        # tracks where to put actual request in
        pnt = 0
        
        # For all current stops in the route
        for s in range(len(stops)): 
            
            stopTime = stops[s][1]
            
            # --- test valid pickup window
            #      If it is +- 45 minutes from requested pick-up time, then that is the window
            if (stopTime > requestTime + self.MIN_SCHEDULE_WINDOW) and (stopTime < requestTime + self.MAX_SCHEDULE_WINDOW):
                
                # Append pick-up option, if before or equal to request time, go before pointer
                #    The logic is that if after, it will be accounted for already
                if requestTime <= stopTime:
                    puOptions.append([s, stopTime])
                    
                # If after request time or equal to, go pointer + 1.
                #     The logic is that if before, it will be accounted for already
                if requestTime >= stopTime:
                    puOptions.append([s+1, stopTime])
                
            # --- used to make sure actual requested time is an option for pickup
            if stopTime <= requestTime:
                # increment until find actual request insert
                pnt = pnt + 1
                
        # --- add actual request time to puOptions if it is not already in there
        if [pnt, requestTime] not in puOptions:
            puOptions.append([pnt, requestTime])
        
        return puOptions
    
    def set_requests(self, requests):
        self.requests = requests


# =================== inline Test ====================
import os
import sys
programPath = os.path.dirname(os.path.abspath("Main.ipynb"))
sys.path.append(programPath + "\\modules")
programPath = os.path.dirname(os.path.abspath("Main.py"))
sys.path.append(programPath + "\\modules")

from Mapper import Mapper

def printStops(stops):
    print()
    print("stops for testing")
    for i in range(len(stops)):
        print(i, "  --> ",stops[i])
        
if __name__ == "__main__":
    mapper = Mapper(programPath)
    algorithms = Algorithms(mapper)
    
    
    stops = [[3, -80, -80, -6, '2114 Lincoln St']]
    stops.append([1, 31, 0, 10, '879 Neon Forest Circle'])
    stops.append([3, 33, 5, 33, '1819 Sunlight Dr'])
    stops.append([2, 35, 30, 45, '1715 Iron Horse Dr'])
    stops.append([1, 45, 45, 60, '2114 Lincoln St'])
    stops.append([2, 80, 80, 90, '1819 Sunlight Dr'])
    printStops(stops)
    print()
    
    request = ['1225 Ken Pratt Blvd', '225 E 8th Ave', 35]
    requestTime = request[2]
    print("request: ", request)
    print()
    
    pickupOptions = algorithms.get_pickupOptions(requestTime, stops)
    print("pickup options: ", pickupOptions)
    print()
    
    options = algorithms.get_dropoffOptions(pickupOptions, stops)
    print("full options")
    for option in options: print(option)
    print()
        
    print("full options but from get_options instead of pickup dropp off.")
    options = algorithms.get_options(requestTime, stops)
    for option in options: print(option)
    print()
        
    # --- algorithms
    #        all algorithms require: routeStops, request
    #            This keeps them uniform in testing
    print()
    print("list algorithms")
    algorithmDict = algorithms.get_algorithms() 
    
    # routeStops, request
    
    
    for key, item in algorithmDict.items():
        options = item(stops, request)
        print(key, options)

        
    print("--- DONE ---")
    
    


# In[ ]:




