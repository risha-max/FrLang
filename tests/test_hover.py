from frlang.lsp.hover import hover_at_position


def test_hover_keyword() -> None:
    doc = hover_at_position("soit nombre x = 1;", 0, 2)
    assert doc is not None
    assert "soit" in doc


def test_hover_type() -> None:
    doc = hover_at_position("soit nombre x = 1;", 0, 8)
    assert doc is not None
    assert "nombre" in doc


def test_hover_mots_method() -> None:
    source = 'soit Mots mot = "abc";\nmot.inverser'
    doc = hover_at_position(source, 1, 8)
    assert doc is not None
    assert "inverser" in doc


def test_hover_ignores_user_variable() -> None:
    doc = hover_at_position("soit nombre x = 1;", 0, 12)
    assert doc is None
