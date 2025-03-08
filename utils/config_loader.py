import os
import yaml

class ConfigLoader:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        self.user_constants = {}

    def load_global_env_vars(self):
        env_config = self.config.get("env", {})
        for key, value in env_config.items():
            os.environ[key] = str(value)

    def load_user_config(self, user: str, broker: str):
        users = self.config.get("users", {})
        if user not in users:
            raise ValueError(f"User '{user}' not found in configuration.")
        user_config = users[user]
        if broker not in user_config:
            raise ValueError(f"Broker '{broker}' configuration for user '{user}' not found.")
        broker_config = user_config[broker]

        env_vars = broker_config.get("env", {})
        for key, value in env_vars.items():
            os.environ[key] = str(value)
        
        self.user_constants = broker_config.get("constant", {})

    def get_user_constant(self, key):
        return self.user_constants.get(key)

    def get_env_var(self, key):
        return os.environ.get(key)

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    config_loader = ConfigLoader(os.path.join(root_dir, "config.yaml"))
    config_loader.load_global_env_vars()
    
    config_loader.load_user_config("junting", "fugle")

    print("FINLAB_API_TOKEN:", os.environ.get("FINLAB_API_TOKEN"))
    print("FUGLE_ACCOUNT:", os.environ.get("FUGLE_ACCOUNT"))
    print("rebalance_safety_weight (from constant):", config_loader.get_user_constant("rebalance_safety_weight"))
    print("strategy_class_name (from constant):", config_loader.get_user_constant("strategy_class_name"))
