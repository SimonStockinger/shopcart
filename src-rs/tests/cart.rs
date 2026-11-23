use shopcart::{Cart, Error, parse_money};

fn sample_cart() -> Cart {
    let mut cart = Cart::new();
    cart.add_item("apple", parse_money("0.50").unwrap(), 4)
        .unwrap();
    cart.add_item("bread", parse_money("2.25").unwrap(), 1)
        .unwrap();
    cart
}

#[test]
fn subtotal() {
    assert_eq!(sample_cart().subtotal().to_string(), "4.25");
}

#[test]
fn add_same_sku_merges() {
    let mut cart = sample_cart();
    cart.add_item("apple", parse_money("0.50").unwrap(), 2)
        .unwrap();
    assert_eq!(cart.items["apple"].quantity, 6);
}

#[test]
fn remove_partial_and_full() {
    let mut cart = sample_cart();
    cart.remove_item("apple", Some(1)).unwrap();
    assert_eq!(cart.items["apple"].quantity, 3);
    cart.remove_item("apple", None).unwrap();
    assert!(!cart.items.contains_key("apple"));
}

#[test]
fn remove_unknown_sku() {
    let mut cart = sample_cart();
    assert_eq!(
        cart.remove_item("x", None),
        Err(Error::UnknownSku("x".into()))
    );
}

#[test]
fn invalid_quantity() {
    let mut cart = sample_cart();
    assert_eq!(
        cart.add_item("x", parse_money("1.00").unwrap(), 0),
        Err(Error::InvalidQuantity)
    );
}

#[test]
fn total_with_discount_and_tax() {
    // 4.25 -> 50% off = 2.13 (half-up) -> +19% tax 0.40 = 2.53
    assert_eq!(
        sample_cart()
            .total("DE", Some("HALFOFF"))
            .unwrap()
            .to_string(),
        "2.53"
    );
}
