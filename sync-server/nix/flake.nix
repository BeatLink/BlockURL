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
                blockurl = pkgs.callPackage ./package.nix { };
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
                devShells.default = pkgs.callPackage ./shell.nix { };
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
                        blockurlPkg = pkgs.callPackage ./package.nix { };
                    };

                nixosModules.default = self.nixosModules.blockurl;
            };
}
