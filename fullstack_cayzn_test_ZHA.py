"""
    Coding test: Bookings report for a transportation operator

    Our revenue management solution CAYZN extracts from an inventory system the transport plan of an operator (trains,
    flights or buses with their itineraries, stops and timetable) and allows our users to analyze sales, forecast the
    demand and optimize their pricing.

    In this project you will manipulate related concepts to build a simple report. We will assess your ability to read
    existing code and to understand the data model in order to develop new features. Two items are essential: the final
    result, and the quality of your code.

    Questions and example data are at the bottom of the script. Do not hesitate to modify existing code if needed.

    Good luck!
"""

import datetime
from typing import List


class Service:
    """A service is a facility transporting passengers between two or more stops at a specific departure date.

    A service is uniquely defined by its number and a departure date. It is composed of one or more legs (which
    represent its stops and its timetable), which lead to multiple Origin-Destination (OD) pairs, one for each possible
    trip that a passenger can buy.
    """

    def __init__(self, name: str, departure_date: datetime.date):
        self.computedItinirary = List[Station]
        self.recomputeItinirary = True
        self.legSET = set()
        self.name = name
        self.departure_date = departure_date
        self.legs: List[Leg] = []
        self.ods: List[OD] = []
        self.stations: List[Station] = []
    @property
    def day_x(self):
        """Number of days before departure.

        In revenue management systems, the day-x scale is often preferred because it is more convenient to manipulate
        compared to dates.
        """
        return (datetime.date.today() - self.departure_date).days
    @property
    def itinerary(self):
        #Si pas de nouvelle insertion d'un leg et que le calcul de l'itiniraire a déja eu lieu
        #Retourner l'initinaire précalculé : computedInitirary
        if self.recomputeItinirary:
            #Sinon
            #Trier les legs par ordre croissant alphabétique sur les noms des stations
            #Ceci pour une condition de sortie rapide lors de la fonction assignNextLeg de la class Leg
            #self.sortLegsByOriginNameAscending()
            for leg in self.legs:
                #La fonction assign next leg trouve le prochain leg correspondant à un leg particulier
                leg.assignNextLeg(self)
            #Assuming legs in a service are properly defined, without inconsistencies
            #Tous les legs ont désormais attachés un prochain leg
            #Cherchons l'origine
            #Nous supprimons toutes les destinations sur une copie de self.legs
            #L'élement restant est donc le depart
            copieLegs = self.legs[:]
            for leg in self.legs:
                if leg.getNextLeg() is not None:
                    copieLegs.remove(leg.getNextLeg())
            depart = copieLegs[0]
            #Nous initialison l'itiniaire computedItinirary
            self.computedItinirary = []
            #Nous commeçons à la gare de départ
            currentLeg = depart

            #Tant que le gare actuelle a une destination
            while True:
                #Nous ajoutons la gare actuelle à l'itinairaire
                self.computedItinirary.append(currentLeg.origin)
                #Si Nous sommes pas au dernier leg
                if currentLeg.getNextLeg() is not None:
                    #Et nous avançons à la prochaine gare
                    currentLeg = currentLeg.getNextLeg()
                else:
                    #Nous sommes au dernier leg
                    #Nous ajoutons la destination (qui est finale)
                    self.computedItinirary.append(currentLeg.destination)
                    break
            self.recomputeItinirary = False
        return self.computedItinirary

    def addLegsNoSort(self, *legs):
        #Ajouter le leg si il n'est pas connu à la liste des legs et au set des legSET
        for leg in legs:
            if leg in self.legSET:
                #Le leg est déjà connu, ne pas ajouter
                pass
            else:
                self.recomputeItinirary = True
                self.legSET.add(leg)
                self.legs.append(leg)

    def load_itinerary(self, itinerary):
        service.legs.clear()
        for idx,station in enumerate(itinerary):
            if idx<len(itinerary)-1:
                service.addLegsNoSort(Leg(service,station,itinerary[idx+1]))
            for j in range(idx+1,len(itinerary)):
                service.ods.append(OD(service,station,itinerary[j]))
        _ = service.itinerary

    def load_passenger_manifest(self, passengers):
        #Dictionnaire temporaire pour faire un "group by" origine et destination (OD)
        #Ceci réduit le nombre de fetch de l'OD correspondant pour initialisier la propriété OD
        #La clé est générée via la concaténation O+D
        temporaryDict={}
        for passenger in passengers:
            key = passenger.origin.name+"$$"+passenger.destination.name
            try:
                temporaryDict[key].append(passenger)
            except:
                temporaryDict[key]=[passenger]
        #Pour chaque clé OD, nous cherchons l'OD correspondant
        for key,value in temporaryDict.items():
            key = key.split("$$")
            originName = key[0]
            destinationName = key[1]
            for od in service.ods:
                if od.origin.name == originName and od.destination.name == destinationName:
                    #Une fois trouvé, nous ajoutons tous les passagers associés à cette OD
                    od.passengers.clear()
                    od.passengers.extend(value)



# def sortLegsByOriginNameAscending(self):
   #    self.legs = sorted(self.legs,key=lambda l: l.origin.name,reverse=False)


class Station:
    """A station is where a service can stop to let passengers board or disembark."""

    def __init__(self, name: str):
        self.name = name


class Leg:
    """A leg is a set of two consecutive stops.

    Example: a service whose itinerary is A-B-C-D has three legs: A-B, B-C and C-D.
    """

    def __init__(self, service: Service, origin: Station, destination: Station):
        self.nextLeg = None
        self.service = service
        self.origin = origin
        self.destination = destination

    def assignNextLeg(self, service):
        possibleLegs = service.legs
        thisDesitination = self.destination
        for leg in possibleLegs:
            if leg.origin == thisDesitination:
                self.nextLeg=leg
                break

    def getNextLeg(self):
        return self.nextLeg

    @property
    def passengers(self):
        passengersOnBoardThisLeg = []
        for od in self.service.ods:
            for loopLeg in od.legs:
                if self == loopLeg:
                    passengersOnBoardThisLeg.extend(od.passengers)
        return  passengersOnBoardThisLeg

class OD:
    """An Origin-Destination (OD) represents the transportation facility between two stops, bought by a passenger.

    Example: a service whose itinerary is A-B-C-D has up to six ODs: A-B, A-C, A-D, B-C, B-D and C-D.
    """

    def __init__(self, service: Service, origin: Station, destination: Station):
        self.service = service
        self.origin = origin
        self.destination = destination
        self.outboundLeg = None
        self.computedLegs = List[Leg]
        self.passengers: List[Passenger] = []
    @property
    def legs(self):
        #Nous parcourons les legs de notre itinéraire
        #Jusqu'à assurer le trajet de l'origine de l'OD jusqu'à la destination de l'OD
        #Nous utiliserons pour ça la fonction getNextLeg de la classe leg à partir de l'origine jusqu'à la destination
        #Trouvons le premier leg à partir du service : outboundLeg
        for loopleg in service.legs:
            if loopleg.origin == self.origin:
                self.outboundLeg = loopleg
                break
        #Depuis l'outboundLeg , en utilisant getNextLeg(), nous parcourons les legs jusqu'à arrivée à destination
        currentLeg = self.outboundLeg
        self.computedLegs = [currentLeg]
        #Tant que le leg actuel ne nous emmène pas vers la destination
        while currentLeg.destination != self.destination:
            #Nous poursuivons sur le prochain leg
            currentLeg = currentLeg.getNextLeg()
            self.computedLegs.append(currentLeg)
        return self.computedLegs

class Passenger:
    """A passenger that has a booking on a seat for a particular origin-destination."""

    def __init__(self, origin: Station, destination: Station, sale_day_x: int, price: float):
        self.origin = origin
        self.destination = destination
        self.sale_day_x = sale_day_x
        self.price = price


# Let's create a service to represent a train going from Paris to Marseille with Lyon as intermediate stop. This service
# has two legs and sells three ODs.


ply = Station("ply")  # Paris Gare de Lyon
lpd = Station("lpd")  # Lyon Part-Dieu
msc = Station("msc")  # Marseille Saint-Charles
service = Service("7601", datetime.date.today() + datetime.timedelta(days=7))
leg_ply_lpd = Leg(service, ply, lpd)
leg_lpd_msc = Leg(service, lpd, msc)
service.legs = [leg_ply_lpd, leg_lpd_msc]
od_ply_lpd = OD(service, ply, lpd)
od_ply_msc = OD(service, ply, msc)
od_lpd_msc = OD(service, lpd, msc)
service.ods = [od_ply_lpd, od_ply_msc, od_lpd_msc]

# 1. Add a property named `itinerary` in `Service` class, that returns the ordered list of stations where the service
# stops. Assume legs in a service are properly defined, without inconsistencies.

# assert service.itinerary == [ply, lpd, msc]
service.stations = [ply, lpd, msc]
assert service.itinerary  == [ply, lpd, msc]
print("Itinerary computation success.")
# 2. Add a property named `legs` in `OD` class, that returns legs that are crossed by this OD. You can use the
# `itinerary` property to find the index of the matching legs.

assert od_ply_lpd.legs == [leg_ply_lpd]
print("Leg computation 1 success.")
assert od_ply_msc.legs == [leg_ply_lpd, leg_lpd_msc]
print("Leg computation 2 success.")
assert od_lpd_msc.legs == [leg_lpd_msc]
print("Leg computation 3 success.")

# 3. Creating every leg and OD for a service is not convenient, to simplify this step, add a method in `Service` class
# to create legs and ODs associated to list of stations. The signature of this method should be:
# load_itinerary(self, itinerary: List["Station"]) -> None:

itinerary = [ply, lpd, msc]
service = Service("7601", datetime.date.today() + datetime.timedelta(days=7))
service.load_itinerary(itinerary)
assert len(service.legs) == 2
print("Leg length success")
assert service.legs[0].origin == ply
print("Leg origin 1 success")
assert service.legs[0].destination == lpd
print("Leg destination 1 success")
assert service.legs[1].origin == lpd
print("Leg origin 2 success")
assert service.legs[1].destination == msc
print("Leg destination 2 success")
assert len(service.ods) == 3
print("ODS success")

od_ply_lpd = next(od for od in service.ods if od.origin == ply and od.destination == lpd)
od_ply_msc = next(od for od in service.ods if od.origin == ply and od.destination == msc)
od_lpd_msc = next(od for od in service.ods if od.origin == lpd and od.destination == msc)

# 4. Create a method in `Service` class that reads a passenger manifest (a list of all bookings made for this service)
# and that allocates bookings across ODs. When called, it should fill the `passengers` attribute of each OD instances
# belonging to the service. The signature of this method should be:
# load_passenger_manifest(self, passengers: List["Passenger"]) -> None:

service.load_passenger_manifest(
     [
         Passenger(ply, lpd, -30, 20),
         Passenger(ply, lpd, -25, 30),
         Passenger(ply, lpd, -20, 40),
         Passenger(ply, lpd, -20, 40),
         Passenger(ply, msc, -10, 50),
     ]
 )
assert len(od_ply_lpd.passengers) == 4
print("Manifest PLY LPD Success")
assert len(od_ply_msc.passengers) == 1
print("Manifest PLY MSC Success")
assert len(od_lpd_msc.passengers) == 0
print("Manifest LPD MSC Success")


#5. Write a property named `passengers` in `Leg` class that returns passengers occupying a seat on this leg.

assert len(service.legs[0].passengers) == 5
print("Leg 1 passenger headcount success")
assert len(service.legs[1].passengers) == 1
print("Leg 2 passenger headcount success")

# 6. We want to generate a report about sales made each day, write a `history()` method in `OD` class that returns a
# list of data point, each data point is a three elements array: [day_x, cumulative number of bookings, cumulative
# revenue].

# history = od_ply_lpd.history()
# assert len(history) == 3
# assert history[0] == [-30, 1, 20]
# assert history[1] == [-25, 2, 50]
# assert history[2] == [-20, 4, 130]

# 7. We want to add to our previous report some forecasted data, meaning how many bookings and revenue are forecasted
# for next days. In revenue management, a number of seats is allocated for each price level. Let's say we only have 5
# price levels from 10€ to 50€. The following variable represents at a particular moment how many seats are available
# (values of the dictionary) at a given price (keys of the dictionary):

# pricing = {10: 0, 20: 2, 30: 5, 40: 5, 50: 5}
# It means we have 2 seats at 20€, 5 at 30€ etc.

# To forecast our bookings, a machine learning algorithm has built the unconstrained demand matrix.
# For each day-x (day before departure) and each price level, this matrix give the expected number of bookings
# to be made:

# demand_matrix = {
#     -7: {10: 5, 20: 1, 30: 0, 40: 0, 50: 0},
#     -6: {10: 5, 20: 2, 30: 1, 40: 1, 50: 1},
#     -5: {10: 5, 20: 4, 30: 3, 40: 2, 50: 1},
#     -4: {10: 5, 20: 5, 30: 4, 40: 3, 50: 1},
#     -3: {10: 5, 20: 5, 30: 5, 40: 3, 50: 2},
#     -2: {10: 5, 20: 5, 30: 5, 40: 4, 50: 3},
#     -1: {10: 5, 20: 5, 30: 5, 40: 5, 50: 4},
#     0: {10: 5, 20: 5, 30: 5, 40: 5, 50: 5}
# }

# 5 days before departure (D-5), if our price is 20€ then 4 bookings can be made that day
# (if we have at least 4 seats to sale at this price level).
# If demand cannot be fulfilled for a particular price, all seats available are sold and demand for new upper prices
# become the initial one minus the booking already made that day.

# For instance, given the previously given `demand_matrix` and `pricing`,
# ----------------------------------------------------------------------
# at D-7, 1 booking will be made at 20€
#   the new pricing is {10: 0, 20: *1*, 30: 5, 40: 5, 50: 5}
#   the new demand_matrix is
# demand_matrix = {
#     -7: {10: 5, 20: *0*, 30: 0, 40: 0, 50: 0},
#     -6: {10: 5, 20: 2, 30: 1, 40: 1, 50: 1},
#     .....
# }

# at D-6, 1 booking will be made at 20€
#   the new pricing is {10: 0, 20: *0*, 30: 5, 40: 5, 50: 5}
#   the new demand_matrix is
# demand_matrix = {
#     -7: {10: 5, 20: 0, 30: 0, 40: 0, 50: 0},
#     -6: {10: 5, 20: *1*, 30: 0, 40: 0, 50: 0},
#     -5: {10: 5, 20: 4, 30: 3, 40: 2, 50: 1},
#     .....
# }

# at D-5, 3 bookings are made at 30€
# and so on...

# Write a `forecast(pricing, demand_matrix)` method in `OD` class to forecast bookings and
# revenue per day-x based on current pricing and demand matrix.

# forecast = od_ply_lpd.forecast(pricing, demand_matrix)
# assert len(forecast) == 8
# assert forecast[0] == [-7, 5, 150.0]
# assert forecast[1] == [-6, 6, 170.0]
# assert forecast[2] == [-5, 9, 260.0]
# assert forecast[3] == [-4, 12, 360.0]
# assert forecast[4] == [-3, 15, 480.0]
# assert forecast[5] == [-2, 18, 620.0]
# assert forecast[6] == [-1, 21, 770.0]
# assert forecast[7] == [0, 21, 770.0]


#https://www.programiz.com/python-programming/online-compiler/