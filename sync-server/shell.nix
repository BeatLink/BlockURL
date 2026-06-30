{
    pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-unstable") { },
}:

pkgs.mkShellNoCC {
    packages = with pkgs; [
        (python3.withPackages (ps: [
            ps.flask
            ps.uvicorn
            ps.asgiref
            ps.peewee
            ps.pytest
            ps.pytest-cov
        ]))
    ];
    shellHook = ''
        echo "BlockURL dev shell ready."
        echo "Start the server with:"
        echo "  python3 -m blockurl"
    '';
}
