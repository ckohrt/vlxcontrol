# VlxControl
VlxControl is a lightweight service that uses [PyVLX](https://github.com/Julius2342/pyvlx) to control io-Homecontrol devices with a Velux KLF 200. It therefore utilizes JSON command/response with AIOHTTP server. Once started, it can be used to control windows, rollershutters, ... from any arbitrary home control software that can execute the curl command.

Installation
------------
Install dependencies and make it executable:

```bash
pip3 install -r requirements.txt
chmod +x vlxcontrol.py
```

Configuration
-------------
Please enter your KLF 200 connection information into the ./pyvlx.yaml configuration file.

Usage
----
```bash
usage: vlxcontrol.py [-h] [-c CONFIG] host port

positional arguments:
  host                  listening address
  port                  listen on this port

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        specify the path to a pyvlx.yaml configuration file
```

Start the service running
```bash
./vlxcontrol.py <listen_address> <port>
```

and make calls using cURL. To close a window, for example, run

```bash
curl -X POST --data "{\"node\":\"windowNameInKlf\", \"position\":100}" --header "Content-Type: application/json" http://<host>:<port>/set
```

to set a device to a position and execute

```bash
curl -s http://<host>:<port>/position/windowNameInKlf
```

to get a device's current positon.

To get a list of all registered devices just issue

```bash
curl -s http://<host>:<port>/devices
```

Setup with OpenHAB
==================

You can use vlxcontrol to control your io-homecontrol devices (like Somfy Dexxo garage door opener or Somfy Oximo rollershutter motor) from OpenHAB. Therefore, you should install the http binding and set up an item similar to this:

```
Rollershutter   MY_ROLLER { http=">[*:POST:http://<host>:<port>/set/<devicename>/%2$s] <[http://<host>:<port>/position/<devicename>:60000:JSONPATH($.position)]" }
```

Then in your sitemap you can define a Slider which can be used to control the device.
