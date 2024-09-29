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
    
    def get_account_name(self):
        return self.config["env"]["FUGLE_ACCOUNT"]
    
    def update_dynamic_params(self, args):
        if args.extra_bid_pct is not None:
            self.config["common"]["extra_bid_pct"] = args.extra_bid_pct

    def _convert_type(self, key, value):
        float_keys = {"extra_bid_pct", "weight"}
        bool_keys = {"view_only"}

        if key in float_keys:
            return float(value)
        elif key in bool_keys:
            return str(value).lower() == "true"
        return value
    
    def get_env_var(self, key):
        return os.environ.get(key)


if __name__ == "__main__":
    config_loader = ConfigLoader()
    config_loader.load_env_vars()

    weight = config_loader.get("weight")
    strategy_class_name = config_loader.get("strategy_class_name")

    print(weight, strategy_class_name)

