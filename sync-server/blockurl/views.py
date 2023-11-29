import html
from flask import jsonify, request
from flask_classful import FlaskView, route


# Index ----------------------------------------------------------------------------------------------------------------
class IndexView(FlaskView):
    route_base = '/'

    def index(self):
        return """
        This is a sync server for BlockURL. <br>
        If you are seeing this message, it has been configured correctly <br>
        See <a href="https://github.com/BeatLink/BlockURL">https://github.com/BeatLink/BlockURL</a> for more information
        """


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
        url = request.get_json()["url"]
        return jsonify(self.database.get_url_exists(url))

    @route('/block', methods=["POST"])
    def block(self):
        url = request.get_json()["url"]
        return jsonify(self.database.set_url(url))

    @route('/unblock', methods=["POST"])
    def unblock(self):
        url = request.get_json()["url"]
        return jsonify(self.database.delete_url(html.unescape(url)))
