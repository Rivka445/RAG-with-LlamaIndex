def test_data_dirs_exist():
    from rag.pipeline import indexer
    from pathlib import Path

    data_dir = indexer.DATA_DIR
    assert isinstance(data_dir, Path)
    assert (data_dir / "cursor").exists()
    assert (data_dir / "claude").exists()
