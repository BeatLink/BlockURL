{
    lib,
    python3,
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

    format = "other"; # not a standard setuptools/pyproject package

    propagatedBuildInputs = [ pythonEnv ];

    # No build step needed — pure Python source
    dontBuild = true;

    installPhase = ''
        runHook preInstall

        # Copy the sync-server application into the output
        mkdir -p $out/lib/blockurl
        cp -r app $out/lib/blockurl/app

        # Write a launcher script
        mkdir -p $out/bin
        cat > $out/bin/blockurl-server <<EOF
        #!${pythonEnv}/bin/python3
        import sys, os
        sys.path.insert(0, "$out/lib/blockurl")
        from app.blockurl import app as application

        if __name__ == "__main__":
            host = os.environ.get("HOST", "0.0.0.0")
            port = int(os.environ.get("PORT", "8000"))
            application.run(host=host, port=port)
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
