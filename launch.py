#!/usr/bin/env python

from subprocess import Popen

client = Popen(["python", "TankWarz_client.py"])
server = Popen(["python", "TankWarz_server.py"])
client.wait()
server.kill()