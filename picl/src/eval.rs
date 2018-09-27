//! The Evaluator is used both by the interpretor and the planned LLVM compiler
//! to convert forms into programs.
use std::collections::HashMap;

use super::env::Environment;
use super::types::LispList;

pub struct Evaluator {
    env:         Environment,
    macro_table: HashMap<String, fn(LispList) -> LispList>,
}

impl Evaluator {
    /// Construct a new Evaluator
    pub fn new() -> Evaluator {
        let env = Environment::new_global_env();
        let macro_table = HashMap::new();
        Evaluator { env, macro_table }
    }

    /// eval is just a stub for now that returns its argument
    pub fn eval(&self, form: String) -> String {
        return form;
    }
}
