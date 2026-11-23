//! Money helpers. All amounts are [`Decimal`]s rounded to cents.

use std::str::FromStr;

use rust_decimal::{Decimal, RoundingStrategy};

use crate::error::Error;

/// Number of decimal places every amount is rounded to.
pub const CENT_PLACES: u32 = 2;

/// Currency code used on receipts.
pub const DEFAULT_CURRENCY: &str = "EUR";

/// Round an amount to cents, half-up (e.g. 2.675 -> 2.68).
///
/// The result always has exactly two decimal places, so it displays as
/// e.g. `5.00` rather than `5`.
pub fn to_money(value: Decimal) -> Decimal {
    let mut rounded =
        value.round_dp_with_strategy(CENT_PLACES, RoundingStrategy::MidpointAwayFromZero);
    rounded.rescale(CENT_PLACES);
    rounded
}

/// Parse a decimal string such as `"2.675"` and round it to cents.
///
/// # Errors
///
/// Returns [`Error::InvalidAmount`] if `value` is not a decimal number.
pub fn parse_money(value: &str) -> Result<Decimal, Error> {
    Decimal::from_str(value)
        .map(to_money)
        .map_err(|_| Error::InvalidAmount(value.to_string()))
}

/// Convert a float to an amount rounded to cents.
///
/// The float goes through its shortest text form first, so that values like
/// `0.1 + 0.2` round as expected (to 0.30).
///
/// # Errors
///
/// Returns [`Error::InvalidAmount`] for NaN, infinity, or values too large
/// for a [`Decimal`].
pub fn money_from_f64(value: f64) -> Result<Decimal, Error> {
    parse_money(&value.to_string())
}

/// Format an amount like `"12.50 EUR"`.
///
/// The amount is rounded with [`to_money`] first.
pub fn format_money(value: Decimal, currency: &str) -> String {
    format!("{} {currency}", to_money(value))
}
