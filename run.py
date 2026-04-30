"""
This file is  responsible as the main entry point
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from web.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
