Example program (we use Rust syntax highlighting, since it's good enough for this syntax).

Fun fact: Github Copilot wrote a large portion of this document.

```rust
var int turns: the value of the field "turns" as read from a file called "config.json"

var int correct_number: a random number between 1 and 100

!: ensure that turns is an integer

fn prompt_user(string prompt) -> int: ask the user for a random number between 1 and 100. return the obtained number

fn main() -> void >
    for [turns]: once for each turn >
        var int guess [prompt_user]: prompt the user

        !: if the guess is correct, given `correct_number`, then exit the loop and inform the user that they have won

    !: inform the user that they have lost
```

# explanation

```rust
var int turns: the value of the field "turns" as read from a file called "config.json"
```

-   `var` indicates a variable declaration.
-   `int` is a type (useful for the purposes of code generation and for reducing ambiguity).
-   `turns` is the name of the variable.
-   `:` indicates that the following text is a description for the AI.
-   In this case, the following text describes the initial value of the variable.

```rust
!: ensure that turns is an integer
```

-   `!` indicates an **action statement**. This can be thought of as a "do this" statement, and its implementation is entirely up to the AI.
-   Once again, `:` indicates that the following text is a description for the AI.

```rust
fn prompt_user(string prompt) -> int: ask the user for a random number between 1 and 100. return the obtained number
```

-   `fn` indicates a function declaration.
-   `prompt_user` is the name of the function.
-   `(string prompt)` is the function's parameters. In this case, the function takes a single parameter, `prompt`, which is a string.
-   `-> int` is the function's return type. In this case, the function returns an integer. Again, this is useful for the purposes of code generation and for reducing ambiguity.
-   The text following `:` describes the behavior of the function.

```rust
fn main() >
```

-   `fn` indicates a function declaration.
-   `main` is the name of the function.
-   `()` indicates that the function takes no parameters.
-   `>` indicates that the body of the function is indented, and is not defined by a natural-language description, but rather by actual Codex code.

```rust
for [turns]: once for each turn >
```

-   `for` indicates a loop.
-   `[turns]:` provides context to the AI generation. In general, providing comma-separated symbol names in the square brackets before a `:` declaration indicates that those symbols should be used in the generated code. In this case, we indicate that the AI should refer to the variable `turns` in the generated code.