from flask import Flask
import argparse


app = Flask(__name__)

app.secret_key = """
Need to see the doctor
but I don't got the cash
Got a pain in my chest
and I hope it would come to pass
but it lingers on and on
"""


@app.route("/")
def ohai():
    return "Hello, luser!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default='0.0.0.0')
    parser.add_argument("--port", "-p", type=int, default=8008)
    parser.add_argument("--no-debug", "-d", default=False, action='store_true')
    options = parser.parse_args()

    debug = not options.no_debug
    app.run(host=options.host, port=options.port, debug=debug)
