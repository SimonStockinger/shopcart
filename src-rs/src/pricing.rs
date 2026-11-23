//! Discount and tax rules.

use rust_decimal::Decimal;

use crate::currency::to_money;
use crate::error::Error;

/// Supported discount codes (upper case) and the fraction taken off.
pub const DISCOUNT_CODES: &[(&str, Decimal)] = &[
    ("WELCOME10", Decimal::from_parts(10, 0, 0, false, 2)),
    ("HALFOFF", Decimal::from_parts(50, 0, 0, false, 2)),
];

/// Supported tax regions (upper case) and their tax rate.
pub const TAX_RATES: &[(&str, Decimal)] = &[
    ("DE", Decimal::from_parts(19, 0, 0, false, 2)),
    ("FR", Decimal::from_parts(20, 0, 0, false, 2)),
    ("US", Decimal::from_parts(0, 0, 0, false, 2)),
];

/// Case-insensitive lookup in one of the rate tables.
fn lookup(table: &[(&str, Decimal)], key: &str) -> Option<Decimal> {
    table
        .iter()
        .find(|(name, _)| name.eq_ignore_ascii_case(key))
        .map(|&(_, rate)| rate)
}

/// Return the subtotal after applying a discount code (case-insensitive).
///
/// If `code` is `None` or empty, no discount is applied. The result is
/// rounded to cents.
///
/// # Errors
///
/// Returns [`Error::UnknownDiscountCode`] if `code` is not in
/// [`DISCOUNT_CODES`].
pub fn apply_discount(subtotal: Decimal, code: Option<&str>) -> Result<Decimal, Error> {
    let subtotal = to_money(subtotal);
    let code = match code {
        Some(code) if !code.is_empty() => code,
        _ => return Ok(subtotal),
    };
    let rate =
        lookup(DISCOUNT_CODES, code).ok_or_else(|| Error::UnknownDiscountCode(code.to_string()))?;
    Ok(to_money(subtotal * (Decimal::ONE - rate)))
}

/// Return the tax owed on `amount` for the given region (case-insensitive).
///
/// This is the tax amount only, not the total including tax, rounded to
/// cents.
///
/// # Errors
///
/// Returns [`Error::UnsupportedRegion`] if `region` is not in [`TAX_RATES`].
pub fn compute_tax(amount: Decimal, region: &str) -> Result<Decimal, Error> {
    let rate =
        lookup(TAX_RATES, region).ok_or_else(|| Error::UnsupportedRegion(region.to_string()))?;
    Ok(to_money(to_money(amount) * rate))
}
