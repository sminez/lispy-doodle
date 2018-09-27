//! PICL a LISP written in Rust
//! It follows and extends the edn format defined by Clojure but it is not
//! Clojure in Rust.

#[macro_use]
extern crate lazy_static;

#[macro_use]
pub mod utils;

// Internal modules
pub mod builtins;
pub mod env;
pub mod eval;
pub mod float;
pub mod interpretor;
pub mod list;
pub mod pmatch;
pub mod read;
pub mod repl;
pub mod types;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
