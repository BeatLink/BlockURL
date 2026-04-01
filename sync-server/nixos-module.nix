{
    config,
    lib,
    blockurlPkg,
    ...
}:

with lib;

let
    cfg = config.services.blockurl;
in
{
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

        extraEnv = mkOption {
            type = types.attrsOf types.str;
            default = { };
            example = literalExpression ''{ FLASK_ENV = "production"; }'';
            description = "Extra environment variables passed to the service process.";
        };

    };

    ##############################################################################
    # Configuration
    ##############################################################################
    config = mkIf cfg.enable {

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

            environment = cfg.extraEnv // {
                BLOCKURL_DATABASE_PATH = "${cfg.dataDir}/${cfg.databaseFile}";
                BLOCKURL_HOST = cfg.host;
                BLOCKURL_PORT = toString cfg.port;
            };

            serviceConfig = {
                Type = "simple";
                User = cfg.user;
                Group = cfg.group;
                ExecStart = "${cfg.package}/bin/blockurl-server";
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
