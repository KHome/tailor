import socket
import json
import logging
from contextlib import contextmanager

from zeroconf import ServiceInfo, Zeroconf

from . import net

logger = logging.getLogger('tailor.zc')


__all__ = [
    'zc_service_context',
    'load_services_from_json']

config = dict()


@contextmanager
def zc_service_context(service_info):
    logger.debug('Attempting to start zc service: "%s"', service_info.name)
    zeroconf = Zeroconf()
    zeroconf.register_service(service_info, ttl=60)
    try:
        yield
    except:
        raise
    finally:
        zeroconf.unregister_service(service_info)
        zeroconf.close()


def new_service_from_json(service_data):
    service_config = service_data['config']
    type_name = service_config['type']
    desc_label = service_config['description'] + '.' + type_name

    addr = socket.inet_aton(config['addr'])
    port = int(config['port'])

    properties = service_config['properties']

    return ServiceInfo(type_name, desc_label, addr, port, 0, 0, properties)


def load_services_from_config():
    # TODO: move to more generic loader
    filename = 'config/server.json'
    with open(filename) as fp:
        json_data = json.load(fp)

    interface_config = json_data['interface']
    config['port'] = interface_config['port']
    config['addr'] = net.guess_local_ip_addresses()

    for service_data in json_data['zeroconf-servers']:
        yield new_service_from_json(service_data)
