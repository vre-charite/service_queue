from app import create_app
from config import ConfigClass
import os

app = create_app()

# add to https
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6060, debug=True)