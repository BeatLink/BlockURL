{
    description = "BlockURL - Firefox extension sync server";

    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs =
        {
            self,
            nixpkgs,
            flake-utils,
        }:

        # --------------------------------------------------------------------------
        # Per-system outputs: package, app, devShell
        # --------------------------------------------------------------------------
        flake-utils.lib.eachDefaultSystem (
            system:
            let
                pkgs = nixpkgs.legacyPackages.${system};
                blockurl = pkgs.callPackage ./package.nix { src = ./.; };
            in
            {
                # --- Packages --------------------------------------------------------
                packages = {
                    blockurl = blockurl;
                    default = blockurl;
                };

                # --- Apps (nix run) --------------------------------------------------
                apps = {
                    blockurl = flake-utils.lib.mkApp {
                        drv = blockurl;
                        name = "blockurl-server";
                    };
                    default = self.apps.${system}.blockurl;
                };

                # --- Dev shell -------------------------------------------------------
                devShells.default = pkgs.mkShell {
                    packages = [
                        (pkgs.python3.withPackages (
                            ps: with ps; [
                                flask
                                # mirror the packages listed in package.nix
                            ]
                        ))
                    ];
                    shellHook = ''
                        echo "BlockURL dev shell ready."
                        echo "Start the server with:"
                        echo "  cd sync-server && DATABASE_PATH=blockurl.db python3 -m app.blockurl"
                    '';
                };
            }
        )

        //
            # --------------------------------------------------------------------------
            # System-independent outputs: NixOS module
            # --------------------------------------------------------------------------
            {
                nixosModules.blockurl =
                    {
                        config,
                        lib,
                        pkgs,
                        ...
                    }:
                    import ./nixos-module.nix {
                        inherit config lib pkgs;
                        # Pass the package built for the module's host system
                        blockurlPkg = pkgs.callPackage ./package.nix { src = ./.; };
                    };

                nixosModules.default = self.nixosModules.blockurl;
            };
}
