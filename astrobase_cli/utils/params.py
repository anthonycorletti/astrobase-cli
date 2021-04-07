import os
from enum import Enum, unique
from pathlib import Path
from typing import Any, Optional

import requests
import yaml
from pydantic import BaseModel


@unique
class YamlFileExtensions(str, Enum):
    yaml = ".yaml"
    yml = ".yml"


class YamlParams(BaseModel):
    """
    Optional params to pass into your yamls.

    Format: key=value<space>key2=value2<space>key3=value3<space>...
    """

    params: Optional[str]

    def as_dict(self) -> dict:
        """
        Return an empty dict if we don't have params or pairs.

        If we have a pair (a=b), return a dict of the pairs {$a: b ...}
        for each (a=b) if b is not None
        """
        if not self.params:
            return {}
        pairs = self.params.split()
        return {
            f"${pair.split('=')[0]}": self.resolve(pair.split("=")[1])
            for pair in pairs
            if pair.split("=")[1] is not None
        }

    def resolve(self, value: str) -> Any:
        if value.isnumeric():
            return int(value)
        return value

    def update_data_with_values(self, data: dict) -> dict:
        """
        Given a data dict, replace env variables, notated as $NAME
        in the string with our params.
        """
        for k, v in self.as_dict().items():
            data = self.replace_var_val(data, k, v)
        return data

    def replace_var_val(self, obj: dict, replace_var: str, replace_value: Any) -> dict:
        for k, v in obj.items():
            if isinstance(v, dict):
                obj[k] = self.replace_var_val(v, replace_var, replace_value)

        for k, v in obj.items():
            if isinstance(v, list):
                for el in v:
                    if isinstance(el, dict):
                        v[v.index(el)] = self.replace_var_val(
                            el, replace_var, replace_value
                        )
                    elif replace_var in v:
                        v[v.index(replace_var)] = replace_value
                        obj[k] = v
            else:
                if v == replace_var:
                    obj[k] = replace_value
        return obj

    def template_resource_files(self, src_dir: str, dst_dir: str) -> None:
        if os.path.isdir(src_dir):
            print("dir")
            for p in Path(src_dir).glob("**/*"):
                if p.suffix in tuple(YamlFileExtensions):
                    f = p.resolve()
                    self.write_parameterized_to_tempdir(f.name, str(f.parent), dst_dir)
        else:
            if src_dir.endswith(tuple(YamlFileExtensions)):
                http = ("https://", "http://")
                if src_dir.startswith(http):
                    res = requests.get(src_dir)
                    with open(
                        f"{dst_dir}/{os.path.basename(src_dir)}", "w"
                    ) as dst_file:
                        dst_file.write(res.content.decode("utf8"))
                else:
                    self.write_parameterized_to_tempdir(
                        os.path.basename(src_dir), str(Path(src_dir).parent), dst_dir
                    )

    def write_parameterized_to_tempdir(
        self, src_file_name: str, src_dir: str, dst_dir: str
    ) -> None:
        with open(f"{dst_dir}/{src_file_name}", "w") as dst_file:
            with open(f"{src_dir}/{src_file_name}", "r") as src_file:
                templated = self.update_data_with_values(yaml.safe_load(src_file))
                final_yaml = yaml.dump(templated, default_flow_style=False)
                dst_file.write(final_yaml)
