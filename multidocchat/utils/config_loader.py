from pathlib import Path
import os
import yaml

def _project_root()-> Path:
    #Just to find the root folder
    # .../utils/config_loader.py -> parents[1] == project root
    return Path(__file__).resolve().parents[1]

def load_config(config_path: str| None= None)-> dict:
    #checking if config folder is presdent then load it otherwisew 
    # load the config parent folder
    env_path = os.getenv("CONFIG_PATH")
    if config_path is None:
        config_path = env_path or str(_project_root()/"config"/"config.yaml")

    path = Path(config_path)
    if not path.is_absolute():
        pathv = _project_root()/path

    if not path.exists():
        raise FileNotFoundError(f"Config file not found:{path}")
    
    with open(path, "r", encoding = "utf-8") as f:
        return yaml.safe_load(f) or {}
    
