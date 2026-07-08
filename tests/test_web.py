from pathlib import Path

from frlang.web.executor import execute_source


def test_execute_main_example(tmp_path: Path) -> None:
    main = tmp_path / "main.frlang"
    main.write_text(
        """
        soit nombre x = 2;
        afficher x;
        """,
        encoding="utf-8",
    )
    result = execute_source(main.read_text(encoding="utf-8"), main)
    assert result.ok is True
    assert result.stdout == ["2"]
    assert result.error is None


def test_execute_reports_error(tmp_path: Path) -> None:
    main = tmp_path / "main.frlang"
    main.write_text("soit nombre x = ;", encoding="utf-8")
    result = execute_source(main.read_text(encoding="utf-8"), main)
    assert result.ok is False
    assert result.error is not None
