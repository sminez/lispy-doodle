//! PICL REPL
//! This is the main Read-Eval-Print-Loop for the PICL interpretor.
//! For the interpretor class itself see intrepretor.rs

extern crate rustyline;

use self::rustyline::Editor;
use self::rustyline::error::ReadlineError;

use super::eval::Evaluator;
use super::read::Reader;

/// A REPL for parsing and evaluating user input
pub struct Repl {
    evaluator: Evaluator,
    reader:    Reader,
}

impl Repl {
    /// Create a new Repl
    pub fn new() -> Repl {
        let evaluator = Evaluator::new();
        let reader = Reader::new();
        Repl { evaluator, reader }
    }

    /// Print a result after interpretation.
    pub fn print(&mut self, string: String) {
        println!("... {}\n", string)
    }

    /// Run the repl, reading input from STDIN with history
    /// At the moment there isn't much functionality being used from
    /// rustyline but there is a lot to check out:
    /// https://github.com/kkawakam/rustyline/blob/master/examples/example.rs
    pub fn repl(&mut self) {
        let mut rl = Editor::<()>::new();
        // Don't worry if there is no history file yet
        if let Err(_) = rl.load_history("/tmp/picl-history.txt") {}

        // READ loop
        loop {
            let readline = rl.readline("λ > ");
            match readline {
                Ok(line) => {
                    rl.add_history_entry(&line);
                    let forms = self.reader.read(line);
                    let value = self.evaluator.eval(forms);
                    self.print(value);
                }

                Err(ReadlineError::Interrupted) => {
                    break; // CTRL-C
                }

                Err(ReadlineError::Eof) => {
                    break; // CTRL-D
                }

                // Some other readline error so report it and bail.
                Err(err) => {
                    println!("Error: {:?}", err);
                    break;
                }
            }
        }
        rl.save_history("/tmp/picl-history.txt").unwrap();
    }
}
