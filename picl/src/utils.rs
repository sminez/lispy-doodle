//! Helper functions and macros for use in the rest of PICL.

// use std::collections::HashMap;

/// A helper for making a HashMap literal.
///
/// # Examples
/// ```
/// let my_map = map!{ "this" => "that", "foo" => "bar" };
/// ```
#[macro_export]
macro_rules! map(
    { $($key:expr => $value:expr),+ } => {
        {
            let mut _map = ::std::collections::HashMap::new();
            $(_map.insert($key, $value);)+
            _map
        }
     };
);
