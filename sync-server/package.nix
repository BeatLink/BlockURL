{
    lib,
    python3,
    uwsgi,
}:
let
    pythonEnv = python3.withPackages (ps: with ps; [ flask ]);
    uwsgiWithPython = uwsgi.override {
        plugins = [ "python3" ];
        python3 = pythonEnv;
    };
in
python3.pkgs.buildPythonApplication {
    pname = "blockurl";
    version = "4.0.6";
    src = ./.;
    format = "pyproject";

    nativeBuildInputs = with python3.pkgs; [
        setuptools
        wheel
    ];
    propagatedBuildInputs = with python3.pkgs; [ flask ];

    postInstall = ''
        mkdir -p $out/etc/blockurl
        cp ${./uwsgi.ini} $out/etc/blockurl/uwsgi.ini

        mkdir -p $out/bin
        cat > $out/bin/blockurl-server << EOF
        #!/bin/sh
        export HOST=\''${HOST:-0.0.0.0}
        export PORT=\''${PORT:-8000}
        export DATABASE_PATH=\''${DATABASE_PATH:-/var/lib/blockurl/blockurl.db}
        exec ${uwsgiWithPython}/bin/uwsgi \
          --ini $out/etc/blockurl/uwsgi.ini \
          --python-home ${pythonEnv}
        EOF
        chmod +x $out/bin/blockurl-server
    '';

    meta = with lib; {
        description = "Sync server for the BlockURL Firefox extension";
        homepage = "https://github.com/BeatLink/BlockURL";
        license = licenses.gpl3Only;
        maintainers = [ "BeatLink" ];
        mainProgram = "blockurl-server";
    };
}
