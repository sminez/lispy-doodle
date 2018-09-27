//! read contains the Reader struct and its associated helpers and data
//! structures.
//!
//! Initial master regex is taken from MAL:
//!   [\s,]*(~@|[\[\]{}()'`~^@]|"(?:\\.|[^\\"])*"|;.*|[^\s\[\]{}('"`,;)]*)
//!
//! https://doc.rust-lang.org/regex/regex/index.html
extern crate regex;

use self::regex::{Captures, Regex};
use std::collections::HashMap;

use super::types::LispVal;

// lazy_static! {
// /// The special quote characters that need additional parsing at the
// reader level pub static ref QUOTES: HashMap<&'static str, LispVal> =
// map!{         "'" => LispVal::Symbol("quote".to_string()),
//         "`" => LispVal::Symbol("quasiquote".to_string()),
//         "~" => LispVal::Symbol("unquote".to_string()),
//         "~@" => LispVal::Symbol("unquote-splicing".to_string())
//     };
// }

// A token used for parsing into internal datatypes
#[derive(Debug)]
struct Token {
    tag:  String,
    text: String,
}

/// A Reader takes string input,either directly or from a file and produces
/// internal data forms.
pub struct Reader {
    regex:  regex::Regex,
    input:  String,
    ix:     i64,
    tokens: Vec<Token>,
}

impl Reader {
    pub fn new() -> Reader {
        // (?x) turns on multi-line and comment mode
        let regex = Regex::new(
            r#"(?x)
            [\s,]*                              # Ignore leading whitespace
            (?P<splice>~@)                      # >> Individual special characters get identified
            |(?P<unquote>~)                     #    here rather than globbing into a single capture
            |(?P<readermacro>\^)                #    group and then further parsing in the main read
            |(?P<quote>')                       #    loop later on.
            |(?P<quasiquote>`)
            |(?P<deref>@)                       # See https://clojuredocs.org/clojure.core/deref
            |(?P<lparen>\()
            |(?P<rparen>\))
            |(?P<lbracket>\[)
            |(?P<rbracket>\])
            |(?P<lcurly>\{)
            |(?P<rcurly>\})
            |(?P<string>"(?:\\.|[^\\"])*")      # String literal
            |(?P<comment>;.*)                   # Comments get discarded
            |(?P<literal>[^\s\[\]{}('"`,;)]*)   # Anything else is a valid literal we need to identify
            |(?P<error>.)                       # If we hit here it's a syntax error
            "#,
        ).unwrap();

        let input = String::new();
        let ix = 0;
        let tokens = Vec::new();

        Reader {
            regex,
            input,
            ix,
            tokens,
        }
    }

    /// read is currently showing the tokens that it finds
    /// It should be changed to return an iterator that can be parsed for the
    /// next step in evaluation.
    pub fn read(&mut self, text: String) -> String {
        self.input = text.clone();
        // iterate over the matches and get our tokens
        let tokens: Vec<Token> = self.regex
            .captures_iter(text.as_str())
            .map(|c| self.get_token(c))
            .collect();

        // XXX :: This is just temporary during development
        println!("{:?}", tokens);

        return text.clone();
    }

    /// Find the group name and build the corresponding token
    fn get_token(&self, c: Captures) -> Token {
        for group in self.regex.capture_names() {
            if let Some(name) = group {
                // This is a named group and not our whitespace discard
                if let Some(text) = c.name(name) {
                    // Pull out the text and return the token
                    return Token {
                        tag:  String::from(name),
                        text: String::from(text.as_str()),
                    };
                }
            }
        }
        // If we had captures to begin with then we've handled it
        unreachable!();
    }
}
