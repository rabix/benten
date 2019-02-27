import shutil
import os
import pathlib
import pytest

from benten.configuration import Configuration
from benten.sbg.profiles import Profiles, ProfileError


test_credential_file_name = "my_credential_file"
sample_credentials_file = \
"""
[default]
api_endpoint = https://api.sbgenomics.com/v2
auth_token   = 671998030559713968361666935769

[cgc]
api_endpoint = https://cgc-api.sbgenomics.com/v2
auth_token   = 282174488599599500573849980909

[cavatica]
api_endpoint = https://cavatica-api.sbgenomics.com/v2
auth_token   = 521419622856657689423872613771

[f4c]
api_endpoint = https://f4c-api.sbgenomics.com/v2
auth_token   = 362736035870515331128527330659

[a bad profile]
"""

test_dir = "./benten-test-config"


def setup():
    with open(test_credential_file_name, "w") as f:
        f.write(sample_credentials_file)


def teardown():
    os.remove(test_credential_file_name)
    shutil.rmtree(pathlib.Path(test_dir), ignore_errors=True)


def test_basic(monkeypatch):
    monkeypatch.setitem(os.environ, "XDG_CONFIG_HOME", test_dir)

    config = Configuration()
    config["sbg"]["credentials_file"] = "does-not-exist"
    prof = Profiles(config=config)

    assert prof.profiles == []

    config["sbg"]["credentials_file"] = test_credential_file_name
    prof = Profiles(config=config)

    assert prof.profiles == ["default", "cgc", "cavatica", "f4c", "a bad profile"]

    api = prof["cgc"]
    assert api.url == "https://cgc-api.sbgenomics.com/v2"
    assert api.token == "282174488599599500573849980909"
    assert api.headers["User-Agent"].startswith("Benten")

    with pytest.raises(KeyError):
        _ = prof["does not exist"]

    with pytest.raises(ProfileError) as e:
        _ = prof["a bad profile"]
        assert e.profile_name == "a bad profile"
