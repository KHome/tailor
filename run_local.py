# -*- coding: utf-8 -*-
"""
script to run a local, self contained server

currently is a candidate to use asyncio
"""
import logging
import time
from subprocess import Popen, call

from platform.unix import release_gvfs_from_camera

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('tailor.launcher')

processes = (
    ('service_cmd', 'apps/service/__main__.py'),
    ('kiosk_server_cmd', 'apps/server/__main__.py'),
    ('kiosk_cmd', 'apps/kiosk/__main__.py'))

# TODO: find python cmd name on whatever platform
python_cmd = '/usr/bin/python3'


# python_cmd = 'C:/python34/python.exe'


# TODO: use subprocess.run


def run_processes():
    for name, cmd in processes:
        logger.debug('starting process %s', name)
        args = [python_cmd, cmd]
        proc = Popen(args)
        time.sleep(5)
        yield proc


if __name__ == '__main__':
    # TODO: check for running in gnome environment
    # TODO: release_gvfs_from_camera fails in windows.  provide better check in future
    try:
        release_gvfs_from_camera()
    except FileNotFoundError:
        pass

    running_processes = list()

    try:
        for proc in run_processes():
            running_processes.append(proc)

        running = True
        while running:
            for proc in running_processes:
                value = proc.poll()
                if value is not None:
                    logger.debug('one process has quit')
                    running = False
                    break
                time.sleep(.1)

    except:
        # TODO: more useful info
        logger.debug('an exception was raised and program will now terminate')

    finally:
        logger.debug('cleaning up...')
        for proc in running_processes:
            try:
                start = time.time()
                while proc.poll() is None:
                    if time.time() - start > 10:
                        break
                    try:
                        proc.terminate()
                        proc.kill()
                    except EnvironmentError:
                        pass

            # TODO: find the correct exception to catch
            except:
                pass

    # werkzerg/flask refuses to close using subprocess
    # so here is my heavy handed hack until i get it
    # figured out
    # TODO: better process cleanup
    try:
        call(['killall', '-KILL', 'python3'], timeout=10)
    except FileNotFoundError:
        pass
