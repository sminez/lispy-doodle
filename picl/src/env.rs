//! Execution environments for PICL to store definitions.
use std::collections::HashMap;

use super::types::LispVal;

/// A recursively defined execution environment
pub struct Environment {
    defs:  HashMap<LispVal, String>,
    outer: Box<Option<Environment>>,
}

impl Environment {
    /// Construct the global environment (should only be called on Evaluator
    /// init)
    pub fn new_global_env() -> Environment {
        let defs = HashMap::new();
        let outer = Box::new(None);
        Environment { defs, outer }
    }

    /// Construct a new nested Environment with and outer Environment.
    pub fn new(outer: Environment) -> Environment {
        let defs = HashMap::new();
        let outer = Box::new(Some(outer));
        Environment { defs, outer }
    }

    /// find attempts to locate the value of the requested symbol in the
    /// closest environment it can see. If the symbol is found, then it
    /// is returned, otherwise None is returned.
    /// NOTE :: At present this is just returning Strings as the LispVal enum
    /// hasn't been implemented yet
    pub fn find(&self, sym: LispVal) -> Option<String> {
        match self.defs.get(&sym) {
            Some(val) => Some(val.clone()),
            None => match *self.outer {
                Some(ref env) => env.find(sym),
                None => None,
            },
        }
    }
}
