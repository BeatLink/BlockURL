{
    lib,
    python3,
    uwsgi,
}:
let
    pythonEnv = python3.withPackages (
        ps: with ps; [
            flask
        ]
    );
in
pythonEnv.pkgs.buildPythonApplication {
    pname = "blockurl";
    version = "4.0.6";
    src = ./.;
    format = "other";

    propagatedBuildInputs = [
        pythonEnv
        uwsgi
    ];

    dontBuild = true;

    installPhase = ''
        runHook preInstall

        # Copy the package into the output
        mkdir -p $out/lib/blockurl
        cp -r ../blockurl $out/lib/blockurl/blockurl
        cp uwsgi.ini $out/lib/blockurl/uwsgi.ini

        # Write a launcher script
        mkdir -p $out/bin
        cat > $out/bin/blockurl-server << EOF
        #!/bin/sh
        export BLOCKURL_HOST=\''${BLOCKURL_HOST:-0.0.0.0}
        export BLOCKURL_PORT=\''${BLOCKURL_PORT:-8000}
        export DATABASE_PATH=\''${DATABASE_PATH:-/var/lib/blockurl/blockurl.db}
        exec ${uwsgi}/bin/uwsgi --ini $out/lib/blockurl/uwsgi.ini --chdir $out/lib/blockurl
        EOF
        chmod +x $out/bin/blockurl-server

        runHook postInstall
    '';

    meta = with lib; {
        description = "Sync server for the BlockURL Firefox extension";
        homepage = "https://github.com/BeatLink/BlockURL";
        license = licenses.gpl3Only;
        maintainers = [ "BeatLink" ];
        mainProgram = "blockurl-server";
    };
}
