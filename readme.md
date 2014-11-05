README

I chose to use a Google Earth visualization in order to present the data in a manner that is very identifiable.  

Fortunately there existed a python library to easily create the KML files used by Google Earth. From there it was relatively simple to receive and parse simulation data with a Python http server and encode the data in a KML. I also added some ways to parse get requests to display the data and serve up the kml files. 

I think in the future, some statistical processing of the data on the server could be useful to identify geographical areas of a similar signal quality, then draw them on the map. So in case there were an area of poor signal quality, a polygon bounding that area could be drawn on the map to indicate it.

Instructions:

Install dependency simplekml:
```bash
pip install simplekml
```

start up the server:
```bash
python server.py
```

run the simulation:
```bash
./sim.bash
```

View the visualization in firefox:
http://localhost:8000/

The visualization provides links to download the google earth browser plugin. You will probably have to adjust the time span in the embedded earth viewer in order to see the data.
From there, the visualization will update every 30 seconds automatically.