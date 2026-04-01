{
    lib,
    python3,
}:
python3.pkgs.buildPythonApplication {
    pname = "blockurl";
    version = "4.0.6";
    src = ./.;
    format = "pyproject";

    nativeBuildInputs = with python3.pkgs; [
        setuptools
        wheel
    ];
    propagatedBuildInputs = with python3.pkgs; [
        flask
        uvicorn
    ];

    meta = with lib; {
        description = "Sync server for the BlockURL Firefox extension";
        homepage = "https://github.com/BeatLink/BlockURL";
        license = licenses.gpl3Only;
        maintainers = [ "BeatLink" ];
        mainProgram = "blockurl-server";
    };
}
