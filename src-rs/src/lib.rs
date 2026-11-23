//! Shopping cart library: add and remove products, apply discount codes,
//! compute regional tax and render a plain-text receipt.
//!
//! All amounts are [`Decimal`]s rounded to cents, half-up (ties away from
//! zero).
//!
//! ```
//! use shopcart::{Cart, parse_money, render_receipt};
//!
//! let mut cart = Cart::new();
//! cart.add_item("apple", parse_money("0.50").unwrap(), 4).unwrap();
//! cart.add_item("bread", parse_money("2.25").unwrap(), 1).unwrap();
//!
//! assert_eq!(cart.total("DE", Some("WELCOME10")).unwrap().to_string(), "4.56");
//! println!("{}", render_receipt(&cart, "DE", Some("WELCOME10")).unwrap());
//! ```

pub mod cart;
pub mod currency;
pub mod error;
pub mod pricing;
pub mod receipt;

pub use cart::{Cart, LineItem};
pub use currency::{DEFAULT_CURRENCY, format_money, money_from_f64, parse_money, to_money};
pub use error::Error;
pub use pricing::{apply_discount, compute_tax};
pub use receipt::render_receipt;
pub use rust_decimal::Decimal;
