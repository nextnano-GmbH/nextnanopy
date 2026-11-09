# No option needs type conversion at config-load time. The only option, 'license', is
# a path kept verbatim: no useful validation exists at load time (see
# decisions_later.md), so validate_config() passes it through untouched.
config_validator = {}

config_default = {"license": ""}
