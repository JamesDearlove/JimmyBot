import urllib.request
import xml.etree.ElementTree as ET

# QLD Precis XML - http://www.bom.gov.au/catalogue/data-feeds.shtml#precis
def get_forecast(location, index):
    data = urllib.request.urlopen("ftp://ftp.bom.gov.au/anon/gen/fwo/IDQ11295.xml").read().decode('utf-8')
    root = ET.fromstring(data)
    for area in root.iter("area"):
        if area.get('description') == location or area.get('aac') == location:
            forecasts = area
            break
    forecast_dict = {
        "location": forecasts.get('description'),
        "index": index,
    }
    for element in forecasts[index]:
        forecast_dict[element.attrib["type"]] = element.text
    return(forecast_dict)

# QLD Observation XML - http://www.bom.gov.au/catalogue/data-feeds.shtml#obs-state
def get_observation(location):
    data = urllib.request.urlopen("ftp://ftp.bom.gov.au/anon/gen/fwo/IDQ60920.xml").read().decode('utf-8')
    root = ET.fromstring(data)
    for station in root.iter("station"):
        if station.get('description') == location:
            observation = station
            break
    observation_dict = {
        "location": observation.get("description"),
        "time-local": observation[0].attrib["time-local"]
    }
    for element in observation[0][0]:
        observation_dict[element.attrib["type"]] = element.text
    return(observation_dict)

def main():
    print(get_forecast("Robina", 1))
    print(get_observation("Coolangatta"))

if __name__ == "__main__":
    main()