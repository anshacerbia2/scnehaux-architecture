from engine.config.loader import deep_update


def test_deep_update():
    d = {"a": 1, "b": {"c": 2}, "l": [1, 2]}
    u = {"a": 2, "b": {"d": 3}, "l": [2, 3], "new": 4}
    res = deep_update(d, u)
    assert res["a"] == 2
    assert res["b"]["c"] == 2
    assert res["b"]["d"] == 3
    assert res["l"] == [1, 2, 3]
    assert res["new"] == 4
