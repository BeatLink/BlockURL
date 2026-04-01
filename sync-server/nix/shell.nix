{
    pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-unstable") { },
}:

pkgs.mkShellNoCC {
    packages = with pkgs; [
        (python3.withPackages (ps: [ ps.flask ]))
    ];
    shellHook = ''
        echo "BlockURL dev shell ready."
        echo "Start the server with:"
        echo "  cd sync-server && DATABASE_PATH=blockurl.db python3 -m blockurl"
    '';
}
