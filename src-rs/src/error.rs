//! Error type shared by all modules.

use std::fmt;

/// Errors returned by the shopcart API.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    /// A text or float value could not be read as an amount.
    InvalidAmount(String),
    /// A quantity of zero was passed to [`Cart::add_item`](crate::Cart::add_item).
    InvalidQuantity,
    /// The SKU is not in the cart.
    UnknownSku(String),
    /// The discount code is not in [`DISCOUNT_CODES`](crate::pricing::DISCOUNT_CODES).
    UnknownDiscountCode(String),
    /// The region is not in [`TAX_RATES`](crate::pricing::TAX_RATES).
    UnsupportedRegion(String),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::InvalidAmount(value) => write!(f, "Invalid amount: {value}"),
            Error::InvalidQuantity => write!(f, "quantity must be positive"),
            Error::UnknownSku(sku) => write!(f, "Unknown SKU: {sku}"),
            Error::UnknownDiscountCode(code) => write!(f, "Unknown discount code: {code}"),
            Error::UnsupportedRegion(region) => write!(f, "Unsupported region: {region}"),
        }
    }
}

impl std::error::Error for Error {}
