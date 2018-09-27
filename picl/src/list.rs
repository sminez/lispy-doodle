//! A singly-linked list implementation for LISP in Rust
//! Adapted from http://cglab.ca/~abeinges/blah/too-many-lists/book/README.html

use std::rc::Rc;

#[derive(Debug, Clone, Hash, PartialEq, Eq)]
pub struct List<T> {
    head: Link<T>,
}

/// Type alias to make life easier with the
type Link<T> = Option<Rc<Pair<T>>>;

/// An individual cons-cell within a linked list
#[derive(Debug, Clone, Hash, PartialEq, Eq)]
struct Pair<T> {
    elem: T,
    rest: Link<T>,
}

pub struct Iter<'a, T: 'a> {
    next: Option<&'a Pair<T>>,
}

impl<T> List<T> {
    /// Make a new empty list
    pub fn new() -> Self {
        List { head: None }
    }

    /// Cons an element onto the head of an existing list
    pub fn cons(&self, elem: T) -> List<T> {
        List {
            head: Some(Rc::new(Pair {
                elem: elem,
                rest: self.head.clone(),
            })),
        }
    }

    /// Take a clone of the tail of a list
    pub fn tail(&self) -> List<T> {
        List {
            head: self.head.as_ref().and_then(|pair| pair.rest.clone()),
        }
    }

    /// Try to exract the head of the list
    pub fn head(&self) -> Option<&T> {
        self.head.as_ref().map(|pair| &pair.elem)
    }

    /// Build an iterator out of this list
    pub fn iter(&self) -> Iter<T> {
        Iter {
            next: self.head.as_ref().map(|pair| &**pair),
        }
    }

    /// Convert to a Vector
    pub fn to_vec(&self) -> Vec<&T> {
        self.iter().collect()
    }
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;

    // Generate the next value of the iterator
    fn next(&mut self) -> Option<Self::Item> {
        self.next.map(|pair| {
            self.next = pair.rest.as_ref().map(|pair| &**pair);
            &pair.elem
        })
    }
}
