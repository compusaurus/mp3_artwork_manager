import pytest
import os
from config import load_config, save_config, CONFIG_FILE, DEFAULT_CONFIG

def test_load_and_save_config(tmp_path):
    test_config_path = tmp_path / CONFIG_FILE
    os.chdir(tmp_path)

    config = load_config()
    assert isinstance(config, dict)
    assert "input_dir" in config

    config["first_launch"] = False
    save_config(config)

    loaded = load_config()
    assert loaded["first_launch"] is False
