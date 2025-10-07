import glob
import importlib
import inspect
import os
import re
import sys
from types import ModuleType
from typing import Any, Dict, Pattern

from pydantic import ValidationError
from pydantic_settings import BaseSettings
from utils.logger import logger

from .db import DBConfig
from .ops import OpsConfig
from .redis import RedisConfig


class BasicConfig:
    OPS = OpsConfig
    DB = DBConfig
    OPS = OpsConfig
    REDIS = RedisConfig

    def __init__(self):
        self._config_data: Dict[str, BaseSettings] = {}

    def __getattr__(self, item: str) -> Any:
        return self.get(item)

    def get(self, key: str) -> Any:
        config = self._config_data
        if isinstance(config, dict) and key in config:
            config = config[key]
        else:
            raise AttributeError(f"Config attribute '{key}' not found")
        return config

    def append_config_module(self, module_name: str, config_module: Any) -> None:
        setattr(self, module_name, config_module)


def resolve_module_name(module_path: str) -> tuple[str, str]:
    _, filename = os.path.split(module_path)
    base_pattern: Pattern[str] = re.compile(r"^(base|config).*")
    # Exclude internal file and file name which start with base or config
    if os.path.basename(filename).startswith("_") or base_pattern.match(
        os.path.basename(filename)
    ):
        return "", ""

    # Get the directory of parent directory name
    parent_dir_name: str = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

    module_base_name, _ = os.path.splitext(os.path.basename(module_path))
    module_name: str = f"{parent_dir_name}.{module_base_name}"
    return module_base_name, module_name


def load_app_config() -> BasicConfig:
    config = BasicConfig()
    folder, _ = os.path.split(os.path.abspath(__file__))
    paths: list[str] = glob.glob(f"{folder}/*.py")
    validation_errors = []

    for path in paths:
        module_base_name, module_name = resolve_module_name(path)
        if not module_base_name:
            continue

        # Dynamically import the module
        module: ModuleType = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseSettings) and obj is not BaseSettings:
                try:
                    config_instance = obj()
                    config.append_config_module(
                        module_base_name.upper(), config_instance
                    )
                except ValidationError as e:
                    validation_errors.append(
                        f"Config ValidationError in {module_name}: {e}"
                    )
                except Exception as e:
                    validation_errors.append(f"Config Error in {module_name}: {e}")
                    logger.error(f"Config Exception in {module_name}: {e}")

    if validation_errors:
        for error in validation_errors:
            logger.error(error)
        sys.exit(1)

    return config


Config = load_app_config()
