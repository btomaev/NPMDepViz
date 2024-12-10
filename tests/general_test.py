import pytest
from unittest.mock import patch, MagicMock
from depviz import _quoted_path, main

def test_quoted_path_with_space():
    path = "path with space"
    assert _quoted_path(path) == '"path with space"'

def test_quoted_path_without_space():
    path = "simplepath"
    assert _quoted_path(path) == 'simplepath'

@patch("argparse.ArgumentParser.parse_args")
@patch("depviz.get_repo")
@patch("depviz.build_deps")
@patch("depviz.genuml")
@patch("os.mkdir")
@patch("os.path.exists", return_value=True)
@patch("subprocess.Popen")
def test_main(mock_popen, mock_exists, mock_mkdir, mock_genuml, mock_build_deps, mock_get_repo, mock_args):
    mock_args.return_value = MagicMock(
        config=None, repo="testrepo", registry="https://registry.npmjs.org/", visualizer=None, out="out"
    )
    mock_get_repo.return_value = ({}, 200)
    mock_build_deps.return_value = iter(["dep1", "dep2"])
    mock_genuml.return_value = "@startuml\n@enduml"
    mock_popen.return_value.wait.return_value = 0
    mock_exists.return_value = True

    main()

    mock_get_repo.assert_called_with("testrepo", "https://registry.npmjs.org/")
    mock_build_deps.assert_called()
    mock_genuml.assert_called()
    mock_mkdir.assert_not_called()

@patch("argparse.ArgumentParser.parse_args")
@patch("subprocess.Popen.wait")
def test_main_no_java(mock_popen_wait, mock_args):
    mock_args.return_value = MagicMock(
        config=None, repo="testrepo", registry="https://registry.npmjs.org/", visualizer=None, out="out"
    )
    mock_popen_wait.return_value = 1

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 8

@patch("argparse.ArgumentParser.parse_args")
def test_main_missing_arguments(mock_args):
    mock_args.return_value = MagicMock(config=None, repo=None, visualizer=None, registry=None, out="out")

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
