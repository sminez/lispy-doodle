PICL - PICL Is Crustacean Lisp
==============================

A LISP written in Rust.

The idea is to write a core in Rust that is just enough to bootstrap the rest
in PICL itself.


### Design ideas wish list
- Simple, consistent API for data manipulation a la Clojure.
- Simple pattern matching (more like destructuring)
- Regex literals `/.*(a|b)/` a la AWK?
  - Following the EDN syntax this should be `#r".*(a|b)"` to signify the start
  start of a regex as a reader level tag.
  - Alternatively, I have always really liked Julia's string macros work
  which seems similar to CL's reader macros and Hy's tag macros:
  ```
  (deftag my_tag (expr) `(~expr ~expr))
  ```
  - In Julia they are defined simply as any macro that is named as a single
  character followed by `_str`. They then get applied when that character is
  prepended to a string literal

  --> `r"a regex literal",  f"x = 3y + 2"`

  - The reader/tag macros on the other hand match the EDN idea and are defined
  as `(defreader ...)` or `(deftag ...)` and then called like so:

  --> `#my-tag FORM`

  - They allow for longer tag names but not the nice string application.
  - ...TBH, why not both?!
  - `https://docs.julialang.org/en/stable/manual/metaprogramming/`
  - `http://docs.hylang.org/en/stable/language/api.html#deftag`
  - `https://gist.github.com/chaitanyagupta/9324402`
