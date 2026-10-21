{
    config,
    lib,
    pkgs,
    blockurlPkg,
    ...
}:

with lib;

let
    cfg = config.services.blockurl;
    hashesFile = pkgs.writeText "blockurl-api-key-hashes.json" (builtins.toJSON cfg.apiKeyHashes);
    authEnabled = cfg.apiKeyHashes != { };
in
{
    imports = [
        (mkRemovedOptionModule [ "services" "blockurl" "apiKeyFile" ] ''
            Each client now has its own key: list their SHA-256 digests in
            services.blockurl.apiKeyHashes and set services.blockurl.storageSecretFile.
        '')
    ];

    ##############################################################################
    # Options
    ##############################################################################
    options.services.blockurl = {

        enable = mkEnableOption "BlockURL sync server";

        package = mkOption {
            type = types.package;
            default = blockurlPkg;
            defaultText = literalExpression "blockurl package from flake";
            description = "The BlockURL server package to use.";
        };

        host = mkOption {
            type = types.str;
            default = "0.0.0.0";
            description = "Address the server will bind to.";
        };

        port = mkOption {
            type = types.port;
            default = 8000;
            description = "TCP port the server listens on.";
        };

        dataDir = mkOption {
            type = types.path;
            default = "/var/lib/blockurl";
            description = "Directory for persistent data (SQLite database).";
        };

        databaseFile = mkOption {
            type = types.str;
            default = "blockurl.db";
            description = "SQLite database filename, relative to dataDir.";
        };

        openFirewall = mkOption {
            type = types.bool;
            default = false;
            description = "Open the server port in the NixOS firewall.";
        };

        user = mkOption {
            type = types.str;
            default = "blockurl";
            description = "System user that runs the service.";
        };

        group = mkOption {
            type = types.str;
            default = "blockurl";
            description = "System group that runs the service.";
        };

        apiKeyHashes = mkOption {
            type = types.attrsOf types.str;
            default = { };
            example = literalExpression ''{ laptop = "9b7b3606...a9ec38"; phone = "..."; }'';
            description = ''
                Client name to the hex SHA-256 digest of that client's API key, made with
                <literal>printf %s KEY | sha256sum</literal>. When set, every request must
                carry one of the keys in its <literal>X-API-Key</literal> header or come from
                a signed-in web session. The digests are not secret and go into the Nix store.
            '';
        };

        storageSecretFile = mkOption {
            type = types.nullOr types.path;
            default = null;
            example = "/run/secrets/blockurl-storage-secret";
            description = ''
                Path to a file holding the secret that signs web session cookies.
                Required when <option>apiKeyHashes</option> is set. It is passed in as a
                systemd credential, so the file may stay readable by root only.
            '';
        };

        extraEnv = mkOption {
            type = types.attrsOf types.str;
            default = { };
            example = literalExpression ''{ NICEGUI_STORAGE_PATH = "/var/lib/blockurl/sessions"; }'';
            description = "Extra environment variables passed to the service process.";
        };

    };

    ##############################################################################
    # Configuration
    ##############################################################################
    config = mkIf cfg.enable {

        assertions = [
            {
                assertion = authEnabled -> cfg.storageSecretFile != null;
                message = "services.blockurl.storageSecretFile must be set when apiKeyHashes is set.";
            }
        ];

        # --- User & group --------------------------------------------------------
        users.users.${cfg.user} = {
            isSystemUser = true;
            group = cfg.group;
            home = cfg.dataDir;
            description = "BlockURL sync server service user";
        };

        users.groups.${cfg.group} = { };

        # --- State directory -----------------------------------------------------
        systemd.tmpfiles.rules = [
            "d '${cfg.dataDir}' 0750 ${cfg.user} ${cfg.group} - -"
        ];

        # --- systemd service -----------------------------------------------------
        systemd.services.blockurl = {
            description = "BlockURL Sync Server";
            after = [ "network.target" ];
            wantedBy = [ "multi-user.target" ];

            environment =
                cfg.extraEnv
                // {
                    BLOCKURL_DATABASE_PATH = "${cfg.dataDir}/${cfg.databaseFile}";
                    BLOCKURL_HOST = cfg.host;
                    BLOCKURL_PORT = toString cfg.port;
                }
                // optionalAttrs authEnabled { BLOCKURL_API_KEY_HASHES_FILE = "${hashesFile}"; }
                // optionalAttrs (cfg.storageSecretFile != null) {
                    # systemd expands %d to the service's credentials directory.
                    BLOCKURL_STORAGE_SECRET_FILE = "%d/storage-secret";
                };

            serviceConfig = {
                Type = "simple";
                User = cfg.user;
                Group = cfg.group;
                ExecStart = "${cfg.package}/bin/blockurl-server";
                WorkingDirectory = cfg.dataDir;
                LoadCredential = lib.optional (
                    cfg.storageSecretFile != null
                ) "storage-secret:${cfg.storageSecretFile}";
                Restart = "on-failure";
                RestartSec = "5s";

                # Hardening
                NoNewPrivileges = true;
                PrivateTmp = true;
                ProtectSystem = "strict";
                ProtectHome = true;
                ReadWritePaths = [ cfg.dataDir ];
                ProtectKernelTunables = true;
                ProtectKernelModules = true;
                ProtectControlGroups = true;
                RestrictAddressFamilies = [
                    "AF_INET"
                    "AF_INET6"
                    "AF_UNIX"
                ];
                LockPersonality = true;
                MemoryDenyWriteExecute = false; # Python requires this to be off
                RestrictRealtime = true;
                SystemCallFilter = [ "@system-service" ];
                SystemCallErrorNumber = "EPERM";
            };
        };

        # --- Firewall ------------------------------------------------------------
        networking.firewall.allowedTCPPorts = mkIf cfg.openFirewall [ cfg.port ];

    };
}
