from Data import UpstocksDataClient
import pytest

uc = UpstocksDataClient

@pytest.mark.parametrize("symbol", "interval", "to_date", "api_version", [(s1, i1, d1, ap1), (s2, i2, d2, ap2)] )
def test_get_historical_data(symbol, interval, to_date, api_version):
    uc.get_historical_data(symbol, interval, to_date, api_version)
