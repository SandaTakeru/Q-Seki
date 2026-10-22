from expression_functions import build_kyuseki_expression


def test_build_expression_defaults_match_kyuseki_html_signature():
    expr = build_kyuseki_expression('境界')

    # point_layer 省略時は空文字、show_total_table は既定 false
    assert "kyuseki_html('境界', '地番', '', '', '点名'" in expr
    assert expr.endswith("1, false, false, 'north', 0.0005)")
