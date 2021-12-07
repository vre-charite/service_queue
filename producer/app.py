from app import create_app
from config import ConfigClass
import os

app = create_app()

# add to https
if __name__ == '__main__':
	app.run(host=ConfigClass.settings.host, port=ConfigClass.settings.port, debug=True)