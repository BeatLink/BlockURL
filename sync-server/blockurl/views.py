import html
from flask import Blueprint, jsonify, request, render_template, session, redirect

MAX_URLS_PER_REQUEST = 10_000
MAX_URL_LENGTH = 2048

# Index ----------------------------------------------------------------------------------------------------------------
index_bp = Blueprint('index', __name__)


@index_bp.route('/')
def index():
    return render_template("index.html")


# Login ----------------------------------------------------------------------------------------------------------------
def init_login(api_key):
    login_bp = Blueprint('login', __name__)

    @login_bp.route('/login', methods=['GET'])
    def login_page():
        return render_template('login.html', error=False)

    @login_bp.route('/login', methods=['POST'])
    def login_submit():
        if request.form.get('api_key', '') == api_key:
            session['authenticated'] = True
            next_path = request.args.get('next', '/')
            if not next_path.startswith('/') or '//' in next_path:
                next_path = '/'
            return redirect(next_path)
        return render_template('login.html', error=True)

    @login_bp.route('/logout')
    def logout():
        session.clear()
        return redirect('/login')

    return login_bp


# Settings -------------------------------------------------------------------------------------------------------------
def init_settings(database):
    settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

    @settings_bp.route('/all', methods=["GET"])
    def all():
        return jsonify(database.get_all_settings())

    @settings_bp.route('/get', methods=["POST"])
    def get():
        body = request.get_json()
        if not body or "key" not in body:
            return jsonify({"error": "missing 'key'"}), 400
        return jsonify(database.get_setting(body["key"]))

    @settings_bp.route('/set', methods=["POST"])
    def post():
        body = request.get_json()
        if not body or "key" not in body or "value" not in body:
            return jsonify({"error": "missing 'key' or 'value'"}), 400
        return jsonify(database.set_setting(body["key"], body["value"]))

    return settings_bp


# URLs -------------------------------------------------------------------------------------------------------------------
def init_urls(database):
    # Same reasoning as init_settings above: build a new Blueprint each call.
    urls_bp = Blueprint('urls', __name__, url_prefix='/urls')

    @urls_bp.route('/all', methods=["GET"])
    def all():
        all_urls = database.get_all_urls()
        return jsonify(all_urls)

    def _parse_urls(body):
        if not body or "urls" not in body:
            return None, (jsonify({"error": "missing 'urls'"}), 400)
        raw = body["urls"]
        if not isinstance(raw, list) or len(raw) > MAX_URLS_PER_REQUEST:
            return None, (jsonify({"error": f"'urls' must be a list of at most {MAX_URLS_PER_REQUEST} items"}), 400)
        if any(not isinstance(u, str) or len(u) > MAX_URL_LENGTH for u in raw):
            return None, (jsonify({"error": f"each URL must be a string of at most {MAX_URL_LENGTH} characters"}), 400)
        return [html.unescape(u) for u in raw], None

    @urls_bp.route('/check', methods=["POST"])
    def check():
        urls, err = _parse_urls(request.get_json())
        if err:
            return err
        return jsonify(database.get_urls_exist(urls))

    @urls_bp.route('/block', methods=["POST"])
    def block():
        urls, err = _parse_urls(request.get_json())
        if err:
            return err
        return jsonify(database.set_urls(urls))

    @urls_bp.route('/unblock', methods=["POST"])
    def unblock():
        urls, err = _parse_urls(request.get_json())
        if err:
            return err
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