{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.nodejs_20
    pkgs.unzip
    pkgs.zip
    pkgs.sqlite
  ];
  env = {
    PYTHONBIN = "${pkgs.python311}/bin/python3.11";
    LANG = "en_US.UTF-8";
  };
}
