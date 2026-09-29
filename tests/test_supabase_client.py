from app.services.supabase_client import resolve_categoria


CATEGORIAS = {
    "vivienda": "uuid-vivienda",
    "alimentación": "uuid-alimentacion",
    "transporte": "uuid-transporte",
    "salud": "uuid-salud",
}


class TestResolveCategoria:
    def test_exact_match(self):
        assert resolve_categoria("vivienda", CATEGORIAS) == "uuid-vivienda"

    def test_exact_match_case_insensitive(self):
        assert resolve_categoria("Vivienda", CATEGORIAS) == "uuid-vivienda"

    def test_exact_match_with_whitespace(self):
        assert resolve_categoria("  vivienda  ", CATEGORIAS) == "uuid-vivienda"

    def test_partial_match_input_in_category(self):
        assert resolve_categoria("transport", CATEGORIAS) == "uuid-transporte"

    def test_partial_match_category_in_input(self):
        assert resolve_categoria("gastos de transporte", CATEGORIAS) == "uuid-transporte"

    def test_no_match_returns_none(self):
        assert resolve_categoria("entretenimiento", CATEGORIAS) is None

    def test_empty_string_matches_first_partial(self):
        # Empty string is contained in any string via Python's `in` operator,
        # so it matches the first category in the dict.
        result = resolve_categoria("", CATEGORIAS)
        assert result is not None
