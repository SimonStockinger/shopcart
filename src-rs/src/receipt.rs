//! Plain-text receipt rendering.

use crate::cart::Cart;
use crate::currency::{DEFAULT_CURRENCY, format_money};
use crate::error::Error;
use crate::pricing::{apply_discount, compute_tax};

/// Render a cart as a plain-text receipt.
///
/// The receipt lists one line per item (sorted by SKU) with quantity and
/// line total, followed by Subtotal, Discount (only if a non-empty code is
/// given), Tax and Total lines. Example:
///
/// ```text
/// apple      x4   2.00 EUR
/// Subtotal       2.00 EUR
/// Tax (DE)       0.38 EUR
/// Total          2.38 EUR
/// ```
///
/// The region is shown in upper case. The result has no trailing newline.
///
/// # Errors
///
/// Returns [`Error::UnsupportedRegion`] or [`Error::UnknownDiscountCode`]
/// if the region or discount code is unknown.
pub fn render_receipt(
    cart: &Cart,
    region: &str,
    discount_code: Option<&str>,
) -> Result<String, Error> {
    let money = |amount| format_money(amount, DEFAULT_CURRENCY);

    // `cart.items` is a BTreeMap keyed by SKU, so this iterates in SKU order.
    let mut lines: Vec<String> = cart
        .items
        .values()
        .map(|item| {
            format!(
                "{:<10} x{:<3} {}",
                item.sku,
                item.quantity,
                money(item.line_total())
            )
        })
        .collect();

    let subtotal = cart.subtotal();
    let discounted = apply_discount(subtotal, discount_code)?;
    let tax = compute_tax(discounted, region)?;
    let tax_label = format!("Tax ({})", region.to_uppercase());

    lines.push(format!("{:<15}{}", "Subtotal", money(subtotal)));
    if discount_code.is_some_and(|code| !code.is_empty()) {
        lines.push(format!(
            "{:<15}-{}",
            "Discount",
            money(subtotal - discounted)
        ));
    }
    lines.push(format!("{tax_label:<15}{}", money(tax)));
    lines.push(format!("{:<15}{}", "Total", money(discounted + tax)));
    Ok(lines.join("\n"))
}
