/// Floating point values can not be ordered / hashed in Rust by default
/// (which is the correct thing to do but annoying if you want dynamically
/// typed sets and hashtables!).
/// This module provides a very lightweight wrapper around f64s that
/// implements ordering and hashing which is `good enough` for PICL.
use std::cmp::Ordering;
use std::fmt;

/// LF64 is a Lisp float64 where NaN is larger than anything else.
/// The underlying f64 value needs to be extracted as follows:
///
/// # Examples
/// ```
/// let my_float = LF64(4.2);
/// println!("{}", 5.1 + my_float.0);
/// ```
#[derive(Clone, Copy, Default, Debug, Hash)]
pub struct LF64(pub f64);

impl PartialEq for LF64 {
    fn eq(&self, other: &LF64) -> bool {
        match (self.0.is_nan(), other.0.is_nan()) {
            (false, false) => self.0 == other.0,
            (true, true) => true,
            _ => false,
        }
    }
}

impl Eq for LF64 {}

impl PartialOrd for LF64 {
    fn partial_cmp(&self, other: &LF64) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for LF64 {
    fn cmp(&self, other: &LF64) -> Ordering {
        match (self.0.is_nan(), other.0.is_nan()) {
            (false, false) => {
                if self.0 < other.0 {
                    Ordering::Less
                } else if self.0 > other.0 {
                    Ordering::Greater
                } else {
                    Ordering::Equal
                }
            }
            (false, true) => Ordering::Less,
            (true, false) => Ordering::Greater,
            (true, true) => Ordering::Equal,
        }
    }
}

impl fmt::Display for LF64 {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}
