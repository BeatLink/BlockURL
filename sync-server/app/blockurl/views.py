import html
from flask import jsonify, request, render_template
from flask_classful import FlaskView, route


# Index ----------------------------------------------------------------------------------------------------------------
class IndexView(FlaskView):
    route_base = '/'

    def index(self):
        return render_template("index.html")


# Settings -------------------------------------------------------------------------------------------------------------
class SettingsView(FlaskView):
    default_methods = ['POST']

    def __init__(self, database):
        self.database = database

    @route('/all', methods=["GET"])
    def all(self):
        return jsonify(self.database.get_all_settings())

    @route('/get', methods=["POST"])
    def get(self):
        key = request.get_json()["key"]
        return jsonify(self.database.get_setting(key))

    @route('/set', methods=["POST"])
    def post(self):
        key = request.get_json()["key"]
        value = request.get_json()["value"]
        return jsonify(self.database.set_setting(key, value))


# URLs -----------------------------------------------------------------------------------------------------------------
class UrlsView(FlaskView):

    def __init__(self, database):
        self.database = database

    @route('/all', methods=["GET"])
    def all(self):
        all_urls = self.database.get_all_urls()
        return jsonify(all_urls)

    @route('/check', methods=["POST"])
    def check(self):
        urls = request.get_json()["urls"]
        return jsonify(self.database.get_urls_exist(urls))

    @route('/block', methods=["POST"])
    def block(self):
        urls = request.get_json()["urls"]
        return jsonify(self.database.set_urls(urls))

    @route('/unblock', methods=["POST"])
    def unblock(self):
        urls = request.get_json()["urls"]
        return jsonify(self.database.delete_urls([html.unescape(url) for url in urls]))
