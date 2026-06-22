from src.ledgerloop.csv_io import load_transactions


def test_load_basic():
    txns = load_transactions("id,amount,date\nt1,100,2026-01-01\nt2,250,2026-01-02\n")
    assert len(txns) == 2 and txns[0].id == "t1" and txns[1].amount == 250


def test_load_header_only_is_empty():
    assert load_transactions("id,amount,date\n") == []
