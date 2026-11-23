use shopcart::{Decimal, Error, apply_discount, compute_tax};

fn d(value: i64) -> Decimal {
    Decimal::from(value)
}

#[test]
fn no_code() {
    assert_eq!(apply_discount(d(100), None).unwrap().to_string(), "100.00");
    assert_eq!(
        apply_discount(d(100), Some("")).unwrap().to_string(),
        "100.00"
    );
}

#[test]
fn code_case_insensitive() {
    assert_eq!(
        apply_discount(d(100), Some("welcome10"))
            .unwrap()
            .to_string(),
        "90.00"
    );
}

#[test]
fn unknown_code() {
    assert_eq!(
        apply_discount(d(100), Some("BOGUS")),
        Err(Error::UnknownDiscountCode("BOGUS".into()))
    );
}

#[test]
fn germany() {
    assert_eq!(compute_tax(d(100), "DE").unwrap().to_string(), "19.00");
}

#[test]
fn lowercase_region() {
    assert_eq!(compute_tax(d(10), "fr").unwrap().to_string(), "2.00");
}

#[test]
fn unsupported_region() {
    assert_eq!(
        compute_tax(d(10), "XX"),
        Err(Error::UnsupportedRegion("XX".into()))
    );
}
