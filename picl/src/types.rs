//! Internal data types for use within PICL
use std::collections::{HashMap, HashSet};
use std::fmt;

use super::float::LF64;
use super::list::List;

/// A LispList is a list of LispVals
pub type LispList = List<LispVal>;


#[derive(Debug, Clone, Hash, PartialEq, Eq)]
pub enum LispVal {
    // Literals
    Nil,
    Bool(bool),
    Str(String),
    Symbol(String),
    Keyword(String),
    Float(LF64),
    Int(i64),
    Complex(LF64, LF64),
    // Collection types
    List(LispList),
    Vector(Vec<LispVal>),
    Map(HashMap<String, LispVal>),
    Set(HashSet<LispVal>),
    // Procedures
    // BuiltinProc(fn(List) -> LispVal, String),
    Proc(Procedure),
}

impl fmt::Display for LispVal {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match *self {
            LispVal::Nil => write!(f, "()"),
            LispVal::Bool(ref v) => match v {
                &true => write!(f, "#t"),
                &false => write!(f, "#f"),
            },
            LispVal::Str(ref v) => write!(f, "\"{}\"", v),
            LispVal::Symbol(ref v) => write!(f, "{}", v),
            LispVal::Keyword(ref v) => write!(f, ":{}", v),
            LispVal::Float(ref v) => write!(f, "{}", v),
            LispVal::Int(ref v) => write!(f, "{}", v),
            LispVal::Complex(ref r, ref c) => write!(f, "{}+i{}", r, c),
            // LispVal::List(ref v) => write!(f, "{}", v),
            // LispVal::Vector(ref v) => write!(f, "{}", v),
            // LispVal::Map(ref v) => write!(f, "{}", v),
            // LispVal::Set(ref v) => write!(f, "{}", v),
            // LispVal::BuiltinProc(v, ref s) => write!(f, "Procedure: {}", s),
            LispVal::Proc(ref v) => write!(f, "{}", v),
        }
    }
}


/// A user defined procedure
/// An execution environment is generated when the procedure is called.
#[derive(Debug, Clone)]
pub struct Procedure {
    name:   String,
    params: LispList,
    body:   LispList,
}

impl fmt::Display for Procedure {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Procedure: {}", self.name)
    }
}
