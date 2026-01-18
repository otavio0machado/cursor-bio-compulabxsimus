{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.nodejs-20_x
    pkgs.unzip
    pkgs.zip
    pkgs.sqlite
    pkgs.libffi
    pkgs.openssl
    pkgs.jq
  ];
  env = {
    PYTHONBIN = "${pkgs.python311}/bin/python3.11";
    LANG = "en_US.UTF-8";
  };
}
