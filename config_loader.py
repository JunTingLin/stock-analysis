import os
import yaml

class ConfigLoader:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)
        
    def load_env_vars(self):
        os.environ.update(self.config.get("env", {}))

    def get(self, key):
        value = self.config["common"].get(key)
        return self._convert_type(key, value)
    
    def update_dynamic_params(self, args):
        if args.extra_bid_pct is not None:
            self.config["common"]["extra_bid_pct"] = args.extra_bid_pct

    def _convert_type(self, key, value):
        if key in ["fund", "flask_server_port"]:
            return int(value)
        elif key == "extra_bid_pct":
            return float(value)
        return value


if __name__ == "__main__":
    config_loader = ConfigLoader()
    config_loader.load_env_vars()

    fund = config_loader.get("fund")
    strategy_class_name = config_loader.get("strategy_class_name")
    flask_server_port = config_loader.get("flask_server_port")

    print(fund, strategy_class_name, flask_server_port)

