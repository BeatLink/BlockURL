import html
from flask import Blueprint, jsonify, request, render_template

# Index ----------------------------------------------------------------------------------------------------------------
index_bp = Blueprint('index', __name__)


@index_bp.route('/')
def index():
    return render_template("index.html")


# Settings -------------------------------------------------------------------------------------------------------------
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


def init_settings(database):
    @settings_bp.route('/all', methods=["GET"])
    def all():
        return jsonify(database.get_all_settings())

    @settings_bp.route('/get', methods=["POST"])
    def get():
        key = request.get_json()["key"]
        return jsonify(database.get_setting(key))

    @settings_bp.route('/set', methods=["POST"])
    def post():
        key = request.get_json()["key"]
        value = request.get_json()["value"]
        return jsonify(database.set_setting(key, value))

    return settings_bp


# URLs -----------------------------------------------------------------------------------------------------------------
urls_bp = Blueprint('urls', __name__, url_prefix='/urls')


def init_urls(database):
    @urls_bp.route('/all', methods=["GET"])
    def all():
        all_urls = database.get_all_urls()
        return jsonify(all_urls)

    @urls_bp.route('/check', methods=["POST"])
    def check():
        urls = [html.unescape(url) for url in request.get_json()["urls"]]
        return jsonify(database.get_urls_exist(urls))

    @urls_bp.route('/block', methods=["POST"])
    def block():
        urls = [html.unescape(url) for url in request.get_json()["urls"]]
        return jsonify(database.set_urls(urls))

    @urls_bp.route('/unblock', methods=["POST"])
    def unblock():
        urls = [html.unescape(url) for url in request.get_json()["urls"]]
        return jsonify(database.delete_urls(urls))

    @urls_bp.route('/sorted', methods=["POST"])
    def sorted_urls():
        body = request.get_json() or {}
        order_by = body.get("order_by", "created_at")
        descending = body.get("descending", True)
        domain = body.get("domain")
        if domain is not None:
            domain = html.unescape(domain)
        try:
            results = database.get_urls_sorted(order_by=order_by, descending=descending, domain=domain)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        return jsonify([
            {"url": url, "domain": domain, "created_at": created_at}
            for url, domain, created_at in results
        ])

    @urls_bp.route('/domains', methods=["GET"])
    def domains():
        return jsonify(database.get_domains_with_counts())

    return urls_bp