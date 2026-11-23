use shopcart::{Cart, Error, parse_money, render_receipt};

fn sample_cart() -> Cart {
    let mut cart = Cart::new();
    cart.add_item("bread", parse_money("2.25").unwrap(), 1)
        .unwrap();
    cart.add_item("apple", parse_money("0.50").unwrap(), 4)
        .unwrap();
    cart
}

#[test]
fn receipt_without_discount() {
    // 4.25 subtotal -> 19% tax 0.81 (half-up) -> total 5.06
    let expected = [
        "apple      x4   2.00 EUR",
        "bread      x1   2.25 EUR",
        "Subtotal       4.25 EUR",
        "Tax (DE)       0.81 EUR",
        "Total          5.06 EUR",
    ]
    .join("\n");
    assert_eq!(
        render_receipt(&sample_cart(), "DE", None).unwrap(),
        expected
    );
}

#[test]
fn receipt_with_discount() {
    // 4.25 -> 10% off = 3.83 (half-up), discount 0.42 -> 19% tax 0.73 -> total 4.56
    let expected = [
        "apple      x4   2.00 EUR",
        "bread      x1   2.25 EUR",
        "Subtotal       4.25 EUR",
        "Discount       -0.42 EUR",
        "Tax (DE)       0.73 EUR",
        "Total          4.56 EUR",
    ]
    .join("\n");
    assert_eq!(
        render_receipt(&sample_cart(), "DE", Some("WELCOME10")).unwrap(),
        expected
    );
}

#[test]
fn items_sorted_by_sku() {
    let receipt = render_receipt(&sample_cart(), "US", None).unwrap();
    let lines: Vec<&str> = receipt.lines().collect();
    assert!(lines[0].starts_with("apple"));
    assert!(lines[1].starts_with("bread"));
}

#[test]
fn region_label_uppercased() {
    assert!(
        render_receipt(&sample_cart(), "fr", None)
            .unwrap()
            .contains("Tax (FR)")
    );
}

#[test]
fn no_discount_line_without_code() {
    assert!(
        !render_receipt(&sample_cart(), "DE", None)
            .unwrap()
            .contains("Discount")
    );
}

#[test]
fn empty_cart() {
    let expected = [
        "Subtotal       0.00 EUR",
        "Tax (US)       0.00 EUR",
        "Total          0.00 EUR",
    ]
    .join("\n");
    assert_eq!(render_receipt(&Cart::new(), "US", None).unwrap(), expected);
}

#[test]
fn unknown_discount_code() {
    assert_eq!(
        render_receipt(&sample_cart(), "DE", Some("BOGUS")),
        Err(Error::UnknownDiscountCode("BOGUS".into()))
    );
}

#[test]
fn unsupported_region() {
    assert_eq!(
        render_receipt(&sample_cart(), "XX", None),
        Err(Error::UnsupportedRegion("XX".into()))
    );
}
