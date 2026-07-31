import os
import sys

sys.path.insert(0, os.getcwd())

from main import dashboard

application = dashboard.server
