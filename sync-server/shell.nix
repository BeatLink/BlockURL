{
    pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-unstable") { },
}:

pkgs.mkShellNoCC {
    packages = with pkgs; [
        (python3.withPackages (ps: [
            ps.nicegui
            ps.peewee
            ps.pytest
            ps.pytest-cov
            ps.httpx
        ]))
    ];
    shellHook = ''
        echo "BlockURL dev shell ready."
        echo "Start the server with:"
        echo "  python3 -m blockurl"
    '';
}
