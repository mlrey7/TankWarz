#!/usr/bin/env python

from subprocess import Popen

client = Popen(["python", "gl2.py"])
server = Popen(["python", "game_server.py"])
client.wait()
server.kill()