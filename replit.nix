{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.nodejs_20
    pkgs.sqlite
    pkgs.lsof
    pkgs.nettools
    pkgs.procps
    pkgs.openssl
    pkgs.zlib
    pkgs.glibcLocales
    pkgs.unzip
    pkgs.zip
  ];
  env = {
    PYTHONBIN = "${pkgs.python311}/bin/python3.11";
    LANG = "en_US.UTF-8";
  };
}
