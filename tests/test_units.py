from exptoolkit.data._datamodel import conversion_factor

def test_basic_conversion():
    assert conversion_factor("m", None, "mm", 0) == 1000


def test_with_normalization():
    assert conversion_factor("m", "s", "mm/s", 1) == 1000


def test_cache():
    conversion_factor.cache_clear()
    conversion_factor("m", None, "mm", 0)
    assert conversion_factor.cache_info().hits == 0  # pylint: disable=no-value-for-parameter

    conversion_factor("m", None, "mm", 0)
    assert conversion_factor.cache_info().hits == 1  # pylint: disable=no-value-for-parameter
