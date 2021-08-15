import io
from flask import Flask
from geopy.geocoders import Nominatim
from pandas import DataFrame
import matplotlib.pyplot as plt
import random
from math import radians, cos, sin, asin, sqrt


class Point:
    def __init__(self, latitude, longitude, address):
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.hamper = None


class Hamper:
    def __init__(self, label):
        self.label = label
        self.itemList = []
        self.centerLat = 0.0
        self.centerLong = 0.0


coordinateGenerater = Nominatim(user_agent="code")
Points = []
Hampers = []
HAMPERCOUNT = 0.0
LINKPREFIX = "https://www.google.com/maps/search/?api=1&query="
CONSTDISTANCE = 1.0


def generateRandomPoints(pointNumber):
    global Points
    Points = []

    print("Points creating !!!")

    for i in range(0, pointNumber):
        # Maslak Coordinates
        randLatitude = random.uniform(41.104950, 41.120710)
        randLongitude = random.uniform(29.007313, 29.026190)

        locationPoint = coordinateGenerater.reverse(str(randLatitude) + "," + str(randLongitude))

        p = Point(randLatitude, randLongitude, locationPoint.address)

        Points.append(p)

    print("Points created !!!")


def getPlotterForPoints(points):
    img = io.BytesIO()
    x = [float(p.latitude) for p in points]
    y = [float(p.longitude) for p in points]
    z = [float(p.hamper) for p in points]

    data = {'x': x, 'y': y}
    df = DataFrame(data, columns=['x', 'y'])
    plt.scatter(df['x'], df['y'], c=z, s=50, alpha=0.5)

    plt.show()
    plt.savefig(img, format='png')
    img.seek(0)

    return img


def haversineDistance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6371 * c  # radius of world
    return km


def optimizePoints():
    global Points
    global Hampers
    global HAMPERCOUNT
    global CONSTDISTANCE

    for point in Points:
        hamper, distance = getClosestHamperWithDistance(point)
        if hamper is not None and distance < CONSTDISTANCE:
            updateHampersAndPoint(point, hamper)

        if point.hamper is None:
            updateHampersAndPoint(point)


def getClosestHamperWithDistance(point):
    global Hampers
    distance = 999999.0
    resultOfHamper = None
    for hamper in Hampers:
        tempDistance = haversineDistance(hamper.centerLong, hamper.centerLat,
                                         point.longitude, point.latitude)
        if distance > tempDistance:
            distance = tempDistance
            resultOfHamper = hamper

    return resultOfHamper, distance


def updateHampersAndPoint(point, hamper=None):
    global HAMPERCOUNT
    global Hampers

    if hamper is None:
        point.hamper = HAMPERCOUNT

        hamper = Hamper(HAMPERCOUNT)
        hamper.itemList.append(point)
        hamper.centerLat = point.latitude
        hamper.centerLong = point.longitude
        hamper.label = HAMPERCOUNT

        Hampers.append(hamper)
        HAMPERCOUNT += 1
    else:
        point.hamper = hamper.label
        hamper.itemList.append(point)
        calculateCenterOfHamper(point, hamper)


def calculateCenterOfHamper(point, hamper):
    hamper.centerLong = ((point.longitude + hamper.centerLong) / 2)
    hamper.centerLat = ((point.latitude + hamper.centerLat) / 2)


def getLink(point):
    return "<a href=" + LINKPREFIX + str(point.latitude) + "," + str(point.longitude) + ">Open in Map</a>"


def printAndReturnHampers():
    global Hampers
    result = ""
    for hamper in Hampers:
        itemCount = 0
        result += "<br>"
        print("SEPETNO#" + str(int(hamper.label)))
        result += "SEPETNO#" + str(int(hamper.label)) + "<br>"
        for point in hamper.itemList:
            print("\t item#" + str(itemCount) + " [" + str(point.latitude) + "," + str(point.longitude) + "] "
                                                                                                          "| " + str(
                point.address) + " | " + LINKPREFIX + str(point.latitude) + "," + str(point.longitude))

            result += " <pre> item#" + str(itemCount) + " [" + str(point.latitude) + "," + str(point.longitude) + "] " \
                      + "| " + str(point.address) + " | " + getLink(point)

            itemCount += 1
        result += "<br>"
    return result


app = Flask(__name__)


@app.route('/plot')
def plot():
    global Points
    generateRandomPoints(50)
    optimizePoints()
    res = printAndReturnHampers()
    getPlotterForPoints(Points)

    return res


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
