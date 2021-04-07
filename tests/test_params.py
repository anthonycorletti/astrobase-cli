import os
import shutil

from astrobase_cli.utils.params import YamlParams

test_root = "tmp"
test_dir = f"{test_root}/testing"


def setupTmpDir():
    os.makedirs(test_dir, exist_ok=True)


def teardownTmpDir():
    shutil.rmtree(test_root)


def test_template_dir():
    setupTmpDir()
    params = YamlParams(params="NGINX_CONTAINER_PORT=11001")
    params.template_resource_files("tests/assets/kubernetes", test_dir)
    teardownTmpDir()


def test_template_file():
    setupTmpDir()
    params = YamlParams(params="NGINX_CONTAINER_PORT=11001")
    params.template_resource_files(
        "tests/assets/kubernetes/nginx-deployment.yaml", test_dir
    )
    teardownTmpDir()


def test_template_remote_file():
    setupTmpDir()
    params = YamlParams(params="NGINX_CONTAINER_PORT=11001")
    params.template_resource_files(
        "https://raw.githubusercontent.com/kubernetes/"
        "dashboard/v2.2.0/aio/deploy/recommended.yaml",
        test_dir,
    )
    teardownTmpDir()


def test_replacer():
    params = YamlParams(params="MY_VAR=11001")
    assert "MY_VAR" not in str(params.replace_var_val({"a": "$MY_VAR"}, "$MY_VAR", "b"))
    assert "MY_VAR" not in str(
        params.replace_var_val({"a": ["$MY_VAR", 2]}, "$MY_VAR", "b")
    )
    assert "MY_VAR" not in str(
        params.replace_var_val({"a": {"nested": ["$MY_VAR", 2]}}, "$MY_VAR", "b")
    )
    assert "MY_VAR" not in str(
        params.replace_var_val(
            {"a": {"nested": [{"nested": "$MY_VAR"}, 2]}}, "$MY_VAR", "b"
        )
    )
    assert "MY_VAR" not in str(
        params.replace_var_val(
            {
                "a": {
                    "nested": [
                        {"nested": "$MY_VAR"},
                        {
                            "so": [
                                "darn",
                                {
                                    "nested": "$MY_VAR",
                                    "how": {
                                        "deep": [
                                            "$MY_VAR",
                                            {"can": ["we", "go", "$MY_VAR"]},
                                        ]
                                    },
                                },
                            ]
                        },
                        2,
                    ]
                }
            },
            "$MY_VAR",
            2,
        )
    )
