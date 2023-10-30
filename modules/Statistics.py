import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from copy import deepcopy

# Project Title: Ride-Share Algorithm Tester 
#
# Author: Richard Kershner
# Completion Date: 2023_10-08
#
# Statistics()
# Description: 
#        -.
# Precondition:
#        Route stops submitted from each algorithm and recorded for computing averages
# Postcondition:
#        1.  Provides statistical output in data frames and graphical format
#        2.  Provides example routes in data frame and graphical formats.        
# Implementation:
#         1.  void addRoutes(list stops, boolane saveDisplay)
#             iterates through stops and calculates, based on order of ID representing request order
#             a.  Travel time for passanger
#             b.  Distance traveled for passanger (drive distance of bus)
#             c.  Drive distance of bus
#                  1.  askew because of rejections.  Maybe only matching valid requests routes
#             d.  Rejected ride count for computing final rejections on average
#             c.  Delta of pickup time from requested time
#
# include files go here (lines included below just an example)
#        ???

class Statistics():
    def __init__(self, mapper, baseName):
        
        self.stats = []
        self.statsDeleteRides = []
        self.columns = ["algoName", "epoch", "totDriveTime", "tot_driveTime_PercIndivTime", "totDriveDistance", "iRideTime", "iDeltaReqPU", "iValid", "indivPerc_rideTime"]
        # stats come in two forms, algorithm with single number and algorithm with array of which request, [1],[2],[3]... etc.
        
        self.sampleRoutes = []
        
        self.mapper = mapper
        self.baseName = baseName

    # ------------------------------------------------------------------- add delete statistics
    # Author(s):  Richard Kershner
    # Description:
    #        add algorithm, epoch, deleted slot, and "down" time that happens when removing a ride
    def add_delete_statistics(self, dStat):
        self.statsDeleteRides.append(dStat)
    
    # ------------------------------------------------------------------- add_route
    # Author(s):  Richard Kershner
    # Description:
    #        addRoute and compute information needed for processing statistics
    #        each list of stops needs a tag for which algorithm was used and which request group processed 
    def add_route(self, algorythmName, epochNo, requests, stops, saveDisplay = False):
        # stops listed [3, -80, -80, -6, '2114 Lincoln St']
        # mapping select route only requires address
        # request ID is [0]
        # requests [address1, address2, time]
        
        # --- save stops to sample route for displaying
        if saveDisplay:
            row = [str(epochNo) + "_" + str(len(requests)) + "_"+ algorythmName, deepcopy(stops)]
            self.sampleRoutes.append(row)
        
        passangers = []
        statsDict = dict()
        lastAddress = stops[0][4]
        
        # === statistics to be tracked ===
        # --- general statistics on whole
        tot_driveTime = 0.0
        tot_driveTime_PercIndivTime = 0.0
        tot_driveDistance = 0.0
        
        # --- individual statistics basaed on which ID or request comes in
        #     Each is computed based on which ID in request
        #             Meaning, request 1 slot, request 2 slot.
        #             The farther in the request, the more likely won't fit and gets rejected
        #     indiv_rideTime ~ How long a passanger is on the vehicle as opposed to if they went straight to destination
        #     indiv_delta_PU_actualTime ~ difference from their requested time to actual time
        #     iValid ~ was a request rejected becauese it didn't fit.
        #          Computed at end
        indiv_rideTime = [0] * len(requests)
        indivPerc_rideTime = [0] * len(requests)
        indiv_delta_PU_actualTime = [0] * len(requests)
        indiv_valid = [0] * len(requests)
        
        
        # === Main processing
        #    for each stop of the vehicle
        passangers = []
        lastAddress = None
        
        # Loop through stops computing statistics for each stop..
        for i in range(len(stops)):
            # get request ID from stops
            ID = int(stops[i][0])
            addressStop = stops[i][4]

            # Processing general route information.  distance & time of TOTAL driver travel
            #    Must exist and not be same address
            if (lastAddress != None) and (lastAddress != addressStop):
                routeInfo = self.mapper.getRouteInfo(lastAddress, addressStop)

                # add each step of the journey to the total
                tot_driveTime += routeInfo["time"]
                tot_driveDistance += routeInfo["distance"]

                # how long is each passanger on the bus
                for p in passangers:
                    indiv_rideTime[p] += routeInfo["time"]



            # Processing route information one passanger at a time.  Add passanger, pick-up
            #    Stats computed of expected (single rider pick-up & drop-off) / (Total ride)
            #       passanger time and distance
            if ID not in passangers:
                passangers.append(ID)

                # Difference of actual time from requsted time.
                indiv_delta_PU_actualTime[ID] = abs(stops[i][1] - requests[ID][2])

                # Records to 1 when individual is picked up, valid pickup
                indiv_valid[ID] = 1

            # if ID already on  board, drop-off
            else:
                passangers = list(filter(lambda p: p!= ID, passangers))
                #requests[ID].append(i)

            # update last stopping address for computing total drive distance
            lastAddress = addressStop
                
            # processing try in loop... keeps crashing
        
        # ----------------- end of stops loop ------------
        
        # =====================  compute indivPerc_rideTime = [0] * len(requests) based on
        for i in range(len(requests)):
            count = 0
            if requests[i][0] != requests[i][1]:
                directRideTime = self.mapper.getRouteInfo(requests[i][0], requests[i][1])['time']
                if directRideTime != 0:
                    indivPerc_rideTime[i] = indiv_rideTime[i] / directRideTime
                    tot_driveTime_PercIndivTime += indivPerc_rideTime[i] 
                    count +=1
            else:
                indivPerc_rideTime[i] = None
            if count != 0:
                tot_driveTime_PercIndivTime = tot_driveTime_PercIndivTime / count
                
        
        # Create row to add to statistical tracking
        # note self.columns has to reflect added columns for data frame
        # *** Columns must match below catagories IN ORDER
        #      self.columns = ["algoName", "epoch", 
        #      "totDriveTime", "tot_driveTime_PercIndivTime", "totDriveDistance", 
        #      "iRideTime", "iDeltaReqPU", "iValid", "indivPerc_rideTime"]
        
        statsRow = [algorythmName, epochNo]
        
        # Add Calcualated values to statsRow
        statsRow.append(tot_driveTime)
        statsRow.append(tot_driveTime_PercIndivTime)
        statsRow.append(tot_driveDistance)
        
        # These are lists appended to the row
        statsRow.append(indiv_rideTime)
        statsRow.append(indiv_delta_PU_actualTime)
        statsRow.append(indiv_valid) 
        statsRow.append(indivPerc_rideTime)

        # add row to over all stats for final computations and graphing
        self.stats.append(statsRow)
        
    # =======================================================================================
    
    # --- Calculate Difference between requested pickup time and actual pickup time
    def calc_diff_request_actual_time(self, df_rawStats):
        df1 = df_rawStats
        df1 = pd.DataFrame(df_rawStats["iDeltaReqPU"].values.tolist())
        df1['algoName'] = df_rawStats['algoName']

        dfMean = df1.groupby('algoName').mean()

        newColumns = [i for i in range(1, len(dfMean.columns)+1)]
        dfMean.columns = newColumns

        fig = dfMean.T.plot(figsize=(12,5), \
            xticks=newColumns, title = self.baseName+' User (Passanger) Difference Request to Actual PickUp Time').get_figure()
        return dfMean, fig
    
    # --- Calculate how far the vehicle drives
    def calc_totDriveDistance(self, df_rawStats):
        
        df1 = df_rawStats

        # create a string column to compare valid rides with matching pattern
        df1['iValid2'] = [''.join(map(str, l)) for l in df_rawStats['iValid']]

        # create a count column, which, for each epoch, needs to be the max.  None max are removed.
        df1['count'] = df1.groupby(["epoch", "iValid2"])["iValid2"].transform("count")
        maxVal = df1['count'].max()
        df1 = df1[df1['count'] == maxVal]
        
        df1_mean = df1[["algoName", "totDriveDistance"]].groupby(by="algoName").mean()
        # ----------------------------------------------------
         # calculate x from what to what for best perspective.  This is done as 1/5 of spread
        minTotDriveDistance = df1_mean['totDriveDistance'].min()
        maxTotDriveDistance = df1_mean['totDriveDistance'].max()

        margin = (maxTotDriveDistance - minTotDriveDistance) / 5
        xMin = 0
        if minTotDriveDistance > margin:
            xMin = minTotDriveDistance - margin
        xMax = maxTotDriveDistance + margin


        df1_mean = df1_mean.sort_values("totDriveDistance", ascending=False)

        fig = df1_mean[["totDriveDistance"]].plot.barh(figsize=(10, 4), \
            position=0.3, xlim=(xMin, xMax), title=self.baseName + "Total Drive Distance").get_figure()
            

        #tot_driveTime_PercIndivTime
        return df1_mean, fig
    
    # --- Calculate total drive time of vehicle as a percentage of expecte time
    def calc_totDriveTime_asPercExpectedTime(self, df_rawStats):
        
        df1 = df_rawStats

        # create a string column to compare valid rides with matching pattern
        df1['iValid2'] = [''.join(map(str, l)) for l in df_rawStats['iValid']]

        # create a count column, which, for each epoch, needs to be the max.  None max are removed.
        df1['count'] = df1.groupby(["epoch", "iValid2"])["iValid2"].transform("count")
        maxVal = df1['count'].max()
        df1 = df1[df1['count'] == maxVal]

        # Get the means for each algorithm for total drvie time and total distance traveled by vehicle
        df1_mean = df1[["algoName", "tot_driveTime_PercIndivTime"]].groupby(by="algoName").mean()[["tot_driveTime_PercIndivTime"]]

        df1_mean = df1_mean.sort_values('tot_driveTime_PercIndivTime', ascending=False)

        # calculate x from what to what for best perspective.  This is done as 1/5 of spread
        minTotDriveTime = df1_mean['tot_driveTime_PercIndivTime'].min()
        maxTotDriveTime = df1_mean['tot_driveTime_PercIndivTime'].max()
        margin = (maxTotDriveTime - minTotDriveTime) / 5
        xMin = 0
        if minTotDriveTime > margin:
            xMin = minTotDriveTime - margin


        fig = df1_mean[['tot_driveTime_PercIndivTime']].plot.barh(figsize=(10, 4), \
                    position=0.3, xlim=(xMin, maxTotDriveTime + margin), title=self.baseName+"Total Drive Percentage of Ride Time").get_figure()


        #tot_driveTime_PercIndivTime
        return df1_mean, fig
    
    # --- Calculate total drive time 
    def calc_totDriveTime(self, df_rawStats):
        
        df1 = df_rawStats

        # create a string column to compare valid rides with matching pattern
        df1['iValid2'] = [''.join(map(str, l)) for l in df_rawStats['iValid']]

        # create a count column, which, for each epoch, needs to be the max.  None max are removed.
        df1['count'] = df1.groupby(["epoch", "iValid2"])["iValid2"].transform("count")
        maxVal = df1['count'].max()
        df1 = df1[df1['count'] == maxVal]
        
        # Get the means for each algorithm for total drvie time and total distance traveled by vehicle
        #df1_mean = df1["algoName","totDriveTime"].groupby(by="algoName").mean()[["totDriveTime"]]
        df1_mean = df1[["algoName", "totDriveTime"]].groupby(by="algoName").mean()
        df1_mean = df1_mean.sort_values('totDriveTime', ascending=False)

        # calculate x from what to what for best perspective.  This is done as 1/5 of spread
        minTotDriveTime = df1_mean['totDriveTime'].min()
        maxTotDriveTime = df1_mean['totDriveTime'].max()
        margin = (maxTotDriveTime - minTotDriveTime) / 5
        xMin = 0
        if minTotDriveTime > margin:
            xMin = minTotDriveTime - margin

        fig = df1_mean[['totDriveTime']].plot.barh(figsize=(10, 4), \
            position=0.3, xlim=(xMin, maxTotDriveTime + margin), title = self.baseName+"Total Drive Time").get_figure()


        #tot_driveTime_PercIndivTime
        return df1_mean, fig
    
    # --- Calculate Passanger's ride time as a percentage of direct time divided by actual time
    def calc_userRideTime_asPerc(self, df_rawStats):
        
        df1 = df_rawStats
        
        df1 = pd.DataFrame(df_rawStats["indivPerc_rideTime"].values.tolist())
        df1['algoName'] = df_rawStats['algoName']

        dfMean = df1.groupby('algoName').mean()

        newColumns = [i for i in range(1, len(dfMean.columns)+1)]
        dfMean.columns = newColumns

        fig = dfMean.T.plot(figsize=(12,5), \
            xticks=newColumns, title = self.baseName+'user Ride Time, Average').get_figure()
        return dfMean, fig
    
    # --- Calculate the number of valid rides for each level of requets
    def calc_validity(self, df_rawStats):
        
        df_iValid = pd.DataFrame(df_rawStats["iValid"].values.tolist())
        df_iValid['algoName'] = df_rawStats['algoName']

        dfMean = df_iValid.groupby('algoName').mean()
        newColumns = [i for i in range(1, len(dfMean.columns) + 1)]
        dfMean.columns = newColumns

        fig = dfMean.T.plot(figsize=(12,5), \
            xticks=newColumns, title = self.baseName+'Valid Requests').get_figure()
        return dfMean, fig
    
    def calcualteFinalStatistics(self):
        print()
        graph_dpi = 300
        subFolder = "output\\" + self.baseName
        
        df_rawStats = pd.DataFrame(self.stats, columns=self.columns)
        
        # =====
        
        pickUpDeltaTime_df, pickUpDeltaTime_graph = self.calc_diff_request_actual_time(df_rawStats)
        pickUpDeltaTime_graph.savefig(subFolder + "PickUpDeltaTime.jpg", bbox_inches='tight', dpi=graph_dpi)
        print()
        print(self.baseName + " PickUp Delta Time from Requested")
        print(pickUpDeltaTime_df)
        
        driveDistance_df, driveDistance_graph = self.calc_totDriveDistance(df_rawStats)
        driveDistance_graph.savefig(subFolder + "DriveDistance.jpg", bbox_inches='tight', dpi=graph_dpi)
        print()
        print(self.baseName + " Drive Total Distance Of Vehicle")
        print(driveDistance_df)
        
        
        driveTime_pAve_df, driveTime_pAve_graph = self.calc_totDriveTime_asPercExpectedTime(df_rawStats)
        driveTime_pAve_graph.savefig(subFolder + "DriveTimeAveragePass.jpg", bbox_inches='tight', dpi=graph_dpi)
        print()
        print(self.baseName + " Total Drive Time Percentages of Vehicle.  Adjusted for Variable Distances")
        print(driveTime_pAve_df)
        
        driveTime_df, driveTime_graph = self.calc_totDriveTime(df_rawStats)
        driveTime_graph.savefig(subFolder + "TotalDriveTime.jpg", bbox_inches='tight', dpi=graph_dpi)
        print()
        print(self.baseName + " Total Drive Time")
        print(driveTime_df)
        
        userRideTimePerc_df, userRideTimePerc_graph = self.calc_userRideTime_asPerc(df_rawStats)
        userRideTimePerc_graph.savefig(subFolder + "UserRideTimePercentage.jpg", bbox_inches='tight', dpi=graph_dpi)
        print()
        print(self.baseName + " User (Passanger) Ride Time as Partial Percentage")
        print(userRideTimePerc_df)
        
        validity_df, validity_graph = self.calc_validity(df_rawStats)
        validity_graph.savefig(subFolder + "RequestsValid.jpg", bbox_inches='tight', dpi=graph_dpi)
        print()
        print(self.baseName + "Valid Request")
        print(validity_df)

    # ------------------------------------------------------------------- display stats if rides are deleted
    # Author(s):  Richard Kershner
    # Description:
    #        Display how deleting a pick-up/drop-off from a route effects the route by algorithm used
    # Complete 2023_10-05
    def displayDeletedStats(self):
        df = pd.DataFrame(self.statsDeleteRides, columns = ["algoName", "epoch", "ID", "d", "deadTime"])
        df_mean = df.groupby(by="algoName").mean()[["deadTime"]]
        print("stats on deleted saved issues")
        print(df_mean.sort_values(by="deadTime"))
        
    # ------------------------------------------------------------------- display ALL select routes (stops)
    # Author(s):  Richard Kershner
    # Description:
    #        Display select routes to show how they come out when driving them
    # Complete 2023_10-05
    def displaySelectRoutes(self):
        # each one is stored as title followed by stops
        for route in self.sampleRoutes:
            print(384, "--------------")
            print(route[0])
            print(route[1])
            self.displaySelectRoute(route[1], route[0])
        
    # ------------------------------------------------------------------- display A route (stops)
    # Author(s):  Richard Kershner
    # Description:
    #        Display select routes to show how they come out when driving them
    # Complete 2023_10-05
    def displaySelectRoute(self, stops, title):
        onBoard = []  # who is currently riding.

        # define colors.  These will be equal to passanger id
        c = ['red', 'orange', 'green', 'blue', 'deeppink', 'gold', 'lawngreen', 'cornflowerblue', 'black']

        markersize = 8

        fig = plt.figure()

        baseLineXs = []
        baseLineYs = []

        passRoutes = dict()

        startsX = []
        startsY = []
        startsC = []
        stopsX = []
        stopsY = []
        stopsC = []

        fig.set_figheight(5)
        fig.set_figwidth(10)
        for pnt in range(len(stops)-1): # plot pickup and drop offs 
            passID = stops[pnt][0]
            address = stops[pnt][4]
            address2 = stops[pnt + 1][4]
            
            Xs = []
            Ys = []
            
            if address == address2:
                Xs, Ys = self.mapper.getAddressXY(address)
            else:
                Xs = self.mapper.getRouteInfo(address, address2)['Xs']
                Ys = self.mapper.getRouteInfo(address, address2)['Ys']

            # X = ( X *  393.46223156039287 ) +  105.2399844
            # Y = ( Y *  947.2038070014495 ) +  -40.0981039
            Xs = np.array(Xs)
            Xs = ( Xs +  105.2399844 ) * 39.346223156039287 
            Ys = np.array(Ys)
            Ys = ( Ys - 40.0981039)  *  9.472038070014495

            # first thing if not on board, needs to be added on board
            if passID not in onBoard:
                onBoard.append(passID)
                startsX.append(Xs[0])
                startsY.append(Ys[0])
                startsC.append(c[passID])
            else: # end of trip and will be departing. 
                stopsX.append(Xs[0])
                stopsY.append(Ys[0])
                stopsC.append(c[passID])
                onBoard.remove(passID) 

            for ID in onBoard:
                baseLineXs = baseLineXs + Xs.tolist()
                baseLineYs = baseLineYs + Ys.tolist()

                adjY = ID * .0017
                adjX = ID * .00097
                if ID not in passRoutes:  passRoutes[ID] = {'X':[], 'Y':[]}

                passRoutes[ID]["X"] = passRoutes[ID]["X"] + (Xs + adjX).tolist()
                passRoutes[ID]["Y"] = passRoutes[ID]["Y"] + (Ys + adjY).tolist()

            # last ride needs an end
            if pnt== len(stops)-2:
                stopsX.append(Xs[-1])
                stopsY.append(Ys[-1])
                stopsC.append(c[onBoard[-1]])            

        # -- print each ID routed, offset so to show colors
        for ID, XY in passRoutes.items():
            plt.plot(XY['Y'], XY['X'], c=c[ID], linewidth=1, zorder=ID+3, alpha=.7)

        plt.scatter(startsY, startsX, marker="^", s=200, c=startsC, zorder=21, alpha=.7)
        plt.scatter(stopsY, stopsX, s=300, c=stopsC, zorder=20, alpha=.7)
        plt.title(title)

        # plot last drop off marker
        #passID = route[-1][0]
        # plt.plot(Xs[0], Ys[0], marker="o", markersize=markersize, markeredgecolor=c[passID], markerfacecolor=c[passID]) 
        
        plt.savefig("output/" + title + ".jpg", bbox_inches='tight', dpi=300)
        plt.show()

    def displayStatistics(self):
        self.calcualteFinalStatistics()
        self.displaySelectRoutes()
        
    
# =================== temp Test ====================
import os
import sys
programPath = os.path.dirname(os.path.abspath("tempTest.ipynb"))
sys.path.append(programPath + "\\modules")
programPath = os.path.dirname(os.path.abspath("tempTest.py"))
sys.path.append(programPath + "\\modules")

def printArrayLines(array):
    for i in range(len(array)):
        print(i, "  --> ",array[i])

if __name__ == "__main__":
    mapper = Mapper(programPath)
    statistics = Statistics(mapper, "baseName_")
                     
    requests = [['879 Neon Forest Circle', '1819 Sunlight Dr', 31]]
    requests.append(['1715 Iron Horse Dr', '1819 Sunlight Dr', 34])
    requests.append(['2114 Lincoln St', '879 Neon Forest Circle', 80])
    print()
    print("Requests for testing")
    printArrayLines(requests)
                       
    stops = [[0, 31, 0, 10, '879 Neon Forest Circle']]
    stops.append([0, 33, 5, 33, '1819 Sunlight Dr'])
    stops.append([1, 35, 30, 45, '1715 Iron Horse Dr'])
    stops.append([2, 45, 45, 60, '2114 Lincoln St'])
    stops.append([1, 80, 80, 90, '1819 Sunlight Dr'])
    stops.append([2, 90, 90, 100, '879 Neon Forest Circle']) 
    
    print("Stops for testing")
    for stop in stops:
        print(stop)
    if True:
        print()
        print([[True, False], [0, 4]])
        print()
        print(" ----")
        # def add_Route(self, algorythmName, epochNo, requstGroup, stops, saveDisplay = False):
        statistics.add_route("algoName", 0, requests, stops, saveDisplay=True)
        print(statistics.sampleRoutes)
        print()
        statistics.displayStatistics()
        
    if False:
        print()
        print(" ------ ")
        statistics.sampleRoutes = [["testThisAlgoHere", stops]]
        statistics.displaySelectRoutes()
    
                       