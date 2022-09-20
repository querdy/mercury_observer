from parser.fix_transaction import _vehicle_number_fix


def test_car_vehicle_number_fix():
    assert _vehicle_number_fix("123") is None
    assert _vehicle_number_fix("м123а") is None
    assert _vehicle_number_fix("м123ам") == "м123ам"
    assert _vehicle_number_fix("м123ам123") == "м123ам"
    assert _vehicle_number_fix("м123ам123rus") == "м123ам"
    assert _vehicle_number_fix("м 123 ам 555 rus") == "м123ам"
    assert _vehicle_number_fix("м 1234 ам 555 rus") != "м123ам"
    assert _vehicle_number_fix("вм 123 ам rus 555") == "м123ам"


def test_trailer_vehicle_number_fix():
    assert _vehicle_number_fix("1234") is None
    assert _vehicle_number_fix("ам1234") == "ам1234"
    assert _vehicle_number_fix("ам123499") == "ам1234"
    assert _vehicle_number_fix("ам 1234") == "ам1234"
    assert _vehicle_number_fix("ам 123499") == "ам1234"
    assert _vehicle_number_fix("ам 1234 99") == "ам1234"
    assert _vehicle_number_fix("ам 1234 rus 99") == "ам1234"
    assert _vehicle_number_fix("м123499") is None
