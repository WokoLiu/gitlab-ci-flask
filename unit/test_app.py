from app import get_hit_count


def test_hit_count():
    count = get_hit_count()
    assert get_hit_count() == count + 1
    assert get_hit_count() == count + 2
    assert get_hit_count() == count + 3
