import json
from collections import defaultdict

from django.shortcuts import render, HttpResponse, redirect
import requests

# Create your views here.

# Home Page
def homePage(request):
    return render(request, 'homePage.html')


def map(request):
    # get data from couchDB url and pass to html
    urlAll = "http://172.26.37.245:5984/twitter/_design/anger/_view/alltweets?group=true"
    urlAngry = "http://172.26.37.245:5984/twitter/_design/anger/_view/angertweets?group=true"

    returnDataAll = requests.get(urlAll)
    returnDataAngry = requests.get(urlAngry)

    dataAll = returnDataAll.json()["rows"]
    dataAngry = returnDataAngry.json()["rows"]

    capitalCityData = {}

    for i in range(0, len(dataAll)):
        capitalCityData[dataAll[i]["key"]] = {"twitter": [dataAngry[i]["value"], dataAll[i]["value"]]}

    # pass data to html
    # return render(request, 'map.html', {'nameInHtml':variable})
    return render(request, 'map.html', {'Dict': json.dumps(capitalCityData)})


def analysis(request):
    # all twitters for daily
    dailyUrlAll = "http://172.26.37.245:5984/twitter/_design/anger/_view/allweektweets?group=true"
    dailyReturnDataAll = requests.get(dailyUrlAll)
    # format: [{key: ["Fri", "Adelaide"], value: 23}, ...]
    dailyDataAll = dailyReturnDataAll.json()["rows"]

    dailyTwittersAll = defaultdict(list)
    for item in dailyDataAll:
        week, city = item["key"]
        quantity = item["value"]
        if week is not None:
            dailyTwittersAll[week].append({"city": city, "quantity": quantity})

    # angry twitters for daily
    dailyUrlAngry = "http://172.26.37.245:5984/twitter/_design/anger/_view/weektweets?group=true"
    dailyReturnDataAngry = requests.get(dailyUrlAngry)
    # format: [{key: ["Fri", "Adelaide"], value: 23}, ...]
    dailyDataAngry = dailyReturnDataAngry.json()["rows"]

    # Tue 少 Brisbane
    dailyTwittersAngry = defaultdict(list)
    for item in dailyDataAngry:
        week, city = item["key"]
        quantity = item["value"]
        if week is not None:
            dailyTwittersAngry[week].append({"city": city, "quantity": quantity})

    # daily angry rate
    dailyRate = defaultdict(list)
    for key in dailyTwittersAll:
        for item in dailyTwittersAll[key]:
            for j in dailyTwittersAngry[key]:
                if item["city"] == j["city"]:
                    rate = 1.0 * j["quantity"] / item["quantity"]
                    dailyRate[key].append({"city": item["city"], "rate": rate})

    # {'Fri': [{'city': 'Adelaide', 'rate': 0.02845287492590397}, {'city': 'Brisbane', 'rate': 0.038461538461538464} .]..}
    # print(dailyRate)

    # [week, ad, bris, mel, per, syd]
    graphDataDaily = [0, 1, 2, 3, 4, 5, 6]

    for key in dailyRate:
        appendDataDaily = [0, 0, 0, 0, 0, 0]
        appendDataDaily[0] = key
        for item in dailyRate[key]:
            if item["city"] == "Adelaide":
                appendDataDaily[1] = item["rate"]
            if item["city"] == "Brisbane":
                appendDataDaily[2] = item["rate"]
            if item["city"] == "Melbourne":
                appendDataDaily[3] = item["rate"]
            if item["city"] == "Perth":
                appendDataDaily[4] = item["rate"]
            if item["city"] == "Sydney":
                appendDataDaily[5] = item["rate"]

        if key == "Mon":
            graphDataDaily[0] = appendDataDaily
        if key == "Tue":
            graphDataDaily[1] = appendDataDaily
        if key == "Wed":
            graphDataDaily[2] = appendDataDaily
        if key == "Thu":
            graphDataDaily[3] = appendDataDaily
        if key == "Fri":
            graphDataDaily[4] = appendDataDaily
        if key == "Sat":
            graphDataDaily[5] = appendDataDaily
        if key == "Sun":
            graphDataDaily[6] = appendDataDaily

    # all twitters for hourly
    hourlyUrlAll = "http://172.26.37.245:5984/twitter/_design/anger/_view/allhourtweets?group=true#"
    hourlyReturnDataAll = requests.get(hourlyUrlAll)
    # format: [{key: ["Fri", "Adelaide"], value: 23}, ...]
    hourlyDataAll = hourlyReturnDataAll.json()["rows"]

    hourlyTwittersAll = defaultdict(list)
    for item in hourlyDataAll:
        week, city = item["key"]
        quantity = item["value"]
        if week is not None:
            hourlyTwittersAll[week].append({"city": city, "quantity": quantity})

    # angry twitters for hourly
    hourlyUrlAngry = "http://172.26.37.245:5984/twitter/_design/anger/_view/hourtweets?group=true#"
    hourlyReturnDataAngry = requests.get(hourlyUrlAngry)
    # format: [{key: ["Fri", "Adelaide"], value: 23}, ...]
    hourlyDataAngry = hourlyReturnDataAngry.json()["rows"]


    hourlyTwittersAngry = defaultdict(list)
    for item in hourlyDataAngry:
        week, city = item["key"]
        quantity = item["value"]
        if week is not None:
            hourlyTwittersAngry[week].append({"city": city, "quantity": quantity})

    # hourly angry rate
    hourlyRate = defaultdict(list)
    for key in hourlyTwittersAll:
        for item in hourlyTwittersAll[key]:
            for j in hourlyTwittersAngry[key]:
                if item["city"] == j["city"]:
                    rate = 1.0 * j["quantity"] / item["quantity"]
                    hourlyRate[key].append({"city": item["city"], "rate": rate})

    # {'00': [{'city': 'Adelaide', 'rate': 0.030425963488843813}, {'city': 'Brisbane', 'rate': 0.03125} ..].}
    # print(hourlyRate)
    # [hour, ad, bris, mel, per, syd]
    graphDataHourly = []

    for key in hourlyRate:
        appendDataHourly = [0, 0, 0, 0, 0, 0]
        appendDataHourly[0] = key + ":00"
        for item in hourlyRate[key]:
            if item["city"] == "Adelaide":
                appendDataHourly[1] = item["rate"]
            if item["city"] == "Brisbane":
                appendDataHourly[2] = item["rate"]
            if item["city"] == "Melbourne":
                appendDataHourly[3] = item["rate"]
            if item["city"] == "Perth":
                appendDataHourly[4] = item["rate"]
            if item["city"] == "Sydney":
                appendDataHourly[5] = item["rate"]

        graphDataHourly.append(appendDataHourly)

    # rate
    urlRate = "http://172.26.37.245:5984/crime/e707e547d5be265da01046da530066e9"
    returnDataRate = requests.get(urlRate)
    # format: [{key: ["Fri", "Adelaide"], value: 23}, ...]
    dataRate = returnDataRate.json()["rows"]

    graphDataRate = []
    for item in dataRate:
        angerLevel = item["angerLevel"]
        stateOffenderRate = item["stateOffenderRate"]
        graphDataRate.append([angerLevel, stateOffenderRate])


    # pao pao
    # get data from couchDB url and pass to html
    urlAll = "http://172.26.37.245:5984/twitter/_design/anger/_view/alltweets?group=true"
    urlAngry = "http://172.26.37.245:5984/twitter/_design/anger/_view/angertweets?group=true"

    returnDataAll = requests.get(urlAll)
    returnDataAngry = requests.get(urlAngry)

    dataAll = returnDataAll.json()["rows"]
    dataAngry = returnDataAngry.json()["rows"]

    capitalCityData = {}

    for i in range(0, len(dataAll)):
        capitalCityData[dataAll[i]["key"]] = {"twitter": [dataAngry[i]["value"], dataAll[i]["value"]]}

    # [aus, melb, sydney, brisbane, perth, adelaide]
    returnPaoPao = ["aus", "melb", "sydney", "brisbane", "perth", "adelaide"]
    totalTwitters = 0
    angryTwitters = 0
    for key in capitalCityData:
        totalTwitters = totalTwitters + capitalCityData[key]["twitter"][1]
        angryTwitters = angryTwitters + capitalCityData[key]["twitter"][0]
        if key == "Adelaide":
            cityRate = 100.0 * capitalCityData[key]["twitter"][0] / capitalCityData[key]["twitter"][1]
            returnPaoPao[5] = cityRate
        if key == "Brisbane":
            cityRate = 100.0 * capitalCityData[key]["twitter"][0] / capitalCityData[key]["twitter"][1]
            returnPaoPao[3] = cityRate
        if key == "Melbourne":
            cityRate = 100.0 * capitalCityData[key]["twitter"][0] / capitalCityData[key]["twitter"][1]
            returnPaoPao[1] = cityRate
        if key == "Perth":
            cityRate = 100.0 * capitalCityData[key]["twitter"][0] / capitalCityData[key]["twitter"][1]
            returnPaoPao[4] = cityRate
        if key == "Sydney":
            cityRate = 100.0 * capitalCityData[key]["twitter"][0] / capitalCityData[key]["twitter"][1]
            returnPaoPao[2] = cityRate
    returnPaoPao[0] = 100.0 * angryTwitters / totalTwitters
	
    return render(request, 'analysis.html', {'DictPaoPao': json.dumps(returnPaoPao), 'DictDaily': json.dumps(graphDataDaily), 'DictHourly': json.dumps(graphDataHourly), 'DictRate': json.dumps(graphDataRate)})
