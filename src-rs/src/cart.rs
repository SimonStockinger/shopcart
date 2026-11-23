//! Shopping cart model.
//!
//! A [`Cart`] holds [`LineItem`]s keyed by SKU and computes subtotals and
//! totals using the discount and tax rules from [`crate::pricing`].

use std::collections::BTreeMap;

use rust_decimal::Decimal;

use crate::currency::to_money;
use crate::error::Error;
use crate::pricing::{apply_discount, compute_tax};

/// A single product entry in a cart.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LineItem {
    /// Stock keeping unit identifying the product.
    pub sku: String,
    /// Price of one unit, rounded to cents.
    pub unit_price: Decimal,
    /// Number of units (always positive).
    pub quantity: u32,
}

impl LineItem {
    /// Return `unit_price * quantity`, rounded to cents.
    pub fn line_total(&self) -> Decimal {
        to_money(self.unit_price * Decimal::from(self.quantity))
    }
}

/// A shopping cart.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Cart {
    /// Line items keyed by SKU. Each SKU appears at most once.
    pub items: BTreeMap<String, LineItem>,
}

impl Cart {
    /// Create an empty cart.
    pub fn new() -> Self {
        Self::default()
    }

    /// Add `quantity` units of a product to the cart.
    ///
    /// If the SKU is already in the cart, its quantity is increased and the
    /// originally stored unit price is kept.
    ///
    /// # Errors
    ///
    /// Returns [`Error::InvalidQuantity`] if `quantity` is zero.
    pub fn add_item(&mut self, sku: &str, unit_price: Decimal, quantity: u32) -> Result<(), Error> {
        if quantity == 0 {
            return Err(Error::InvalidQuantity);
        }
        self.items
            .entry(sku.to_string())
            .and_modify(|item| item.quantity += quantity)
            .or_insert_with(|| LineItem {
                sku: sku.to_string(),
                unit_price: to_money(unit_price),
                quantity,
            });
        Ok(())
    }

    /// Remove units of a product from the cart.
    ///
    /// If `quantity` is `None`, or at least the quantity in the cart, the
    /// whole line item is removed.
    ///
    /// # Errors
    ///
    /// Returns [`Error::UnknownSku`] if `sku` is not in the cart.
    pub fn remove_item(&mut self, sku: &str, quantity: Option<u32>) -> Result<(), Error> {
        let item = self
            .items
            .get_mut(sku)
            .ok_or_else(|| Error::UnknownSku(sku.to_string()))?;
        match quantity {
            Some(quantity) if quantity < item.quantity => item.quantity -= quantity,
            _ => {
                self.items.remove(sku);
            }
        }
        Ok(())
    }

    /// Return the sum of all line totals, before discount and tax.
    pub fn subtotal(&self) -> Decimal {
        to_money(self.items.values().map(LineItem::line_total).sum())
    }

    /// Return the final amount to pay.
    ///
    /// The discount is applied to the subtotal first; tax is then computed
    /// on the discounted amount and added.
    ///
    /// # Errors
    ///
    /// Returns [`Error::UnsupportedRegion`] or [`Error::UnknownDiscountCode`]
    /// if the region or discount code is unknown.
    pub fn total(&self, region: &str, discount_code: Option<&str>) -> Result<Decimal, Error> {
        let discounted = apply_discount(self.subtotal(), discount_code)?;
        Ok(to_money(discounted + compute_tax(discounted, region)?))
    }
}
