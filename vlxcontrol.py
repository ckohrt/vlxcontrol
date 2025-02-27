#! /usr/bin/env python3

import subprocess
import asyncio
import json
import time
import argparse
import re
from aiohttp import web
from bottle import run, post, request, response, get, route
from pyvlx import Position, PyVLX

parser = argparse.ArgumentParser()
parser.add_argument("host", help="listening address")
parser.add_argument("port", help="listen on this port")
parser.add_argument(
    "-c", "--config", help="specify the path to a pyvlx.yaml configuration file")
args = parser.parse_args()

host = args.host
port = int(args.port)

routes = web.RouteTableDef()


async def init_pyvlx_connection(loop):
    global pyvlx
    klf_host = args.config
    if (klf_host == None):
        klf_host = "./pyvlx.yaml"

    pyvlx = PyVLX(klf_host, loop=loop)
    await pyvlx.load_nodes()


@routes.post('/set/{device}/{position}')
async def url_set(request):
    try:
        NODE = request.match_info.get('device')
        POS = int(request.match_info.get('position'))
    except:
        response = {'result': 'fail',
                    'reason': 'node or position not provided'}
        return web.json_response(response)

    try:
        await pyvlx.nodes[NODE].set_position(Position(position_percent=POS), wait_for_completion=False)
    except KeyError:
        response = {'result': 'fail', 'reason': 'device unknown'}
        return web.json_response(response)
    except Exception as e:
        response = {'result': 'fail',
                    'reason': 'exception during execution', 'message': str(e)}
        return web.json_response(response)

    newPos = pyvlx.nodes[NODE].position
    data = {'result': 'ok', 'device': NODE, 'position': str(newPos)}
    return web.json_response(data)


@routes.post('/stop/{device}')
async def url_stop(request):
    try:
        NODE = request.match_info.get('device')
        await pyvlx.nodes[NODE].stop()
    except:
        response = {'result': 'fail',
                    'reason': 'node or position not provided'}
        return web.json_response(response)

    newPos = pyvlx.nodes[NODE].position
    data = {'result': 'ok', 'device': NODE, 'position': str(newPos)}
    return web.json_response(data)


@routes.post('/set')
async def handle(request):
    reqType = request.content_type
    if (reqType != 'application/json'):
        response = {'result': 'fail', 'reason': 'unsupported request type'}
        return web.json_response(response)

    message = await request.json()

    try:
        NODE = message['node']
        POS = int(message['position'])
    except:
        response = {'result': 'fail',
                    'reason': 'node or position not provided'}
        return web.json_response(response)

    try:
        await pyvlx.nodes[NODE].set_position(Position(position_percent=POS), wait_for_completion=False)
    except KeyError:
        response = {'result': 'fail', 'reason': 'device unknown'}
        return web.json_response(response)
    except Exception as e:
        response = {'result': 'fail',
                    'reason': 'exception during execution', 'message': str(e)}
        return web.json_response(response)

    newPos = pyvlx.nodes[NODE].position
    data = {'result': 'ok', 'device': NODE, 'position': str(newPos)}
    return web.json_response(data)


@routes.get('/position/{device}')
async def get_position(request):
    try:
        device_name = request.match_info.get('device', None)
        device = pyvlx.nodes[device_name]
        pos = int(get_position(device).replace("%", ""))
    except KeyError:
        response = {'result': 'fail', 'reason': 'device unknown'}
        return web.json_response(response)
    except Exception as e:
        response = {'result': 'fail',
                    'reason': 'exception during execution', 'message': str(e)}
        return web.json_response(response)

    data = {'result': 'ok', 'device': device_name, 'position': pos}
    return web.json_response(data)


@routes.get('/devices')
async def get_devices(request):
    try:
        data = {'result': 'ok', 'devices': []}
        for node in pyvlx.nodes:
            nodetype = str(type(node).__name__)
            if (str(node.position) == 'UNKNOWN'):
                data['devices'].append(
                    {'id': node.node_id, 'name': node.name, 'type': nodetype})
            else:
                pos = int(get_position(node))
                data['devices'].append(
                    {'id': node.node_id, 'name': node.name, 'type': nodetype, 'position': pos})
        return web.json_response(data)
    except Exception as e:
        response = {'result': 'fail'}
        return web.json_response(response)


def get_position(device):
    return re.sub("\D", "", str(device.position))


if __name__ == '__main__':
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(init_pyvlx_connection(LOOP))

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host=host, port=port)
