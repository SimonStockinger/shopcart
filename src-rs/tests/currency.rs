use shopcart::{Decimal, Error, format_money, money_from_f64, parse_money};

#[test]
fn rounds_half_up() {
    assert_eq!(parse_money("2.675").unwrap().to_string(), "2.68");
}

#[test]
fn float_input() {
    assert_eq!(money_from_f64(0.1 + 0.2).unwrap().to_string(), "0.30");
}

#[test]
fn format() {
    assert_eq!(format_money(Decimal::from(5), "EUR"), "5.00 EUR");
    assert_eq!(format_money(parse_money("3.5").unwrap(), "USD"), "3.50 USD");
}

#[test]
fn invalid_amount() {
    assert_eq!(parse_money("abc"), Err(Error::InvalidAmount("abc".into())));
    assert!(money_from_f64(f64::NAN).is_err());
}
