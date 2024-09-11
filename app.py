from flask import Flask
from controllers.stock_controller import stock_blueprint
STATIC_FOLDER = 'templates/assets'

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__,static_folder=STATIC_FOLDER)

# Register the stock blueprint
app.register_blueprint(stock_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
