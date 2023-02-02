# Codex

Codex is a concept programing language powered by the OpenAI generative model of the same name.

## Introduction

> **Warning:** Codex is a heavily experimental concept language, and it is not intended for production use or for writing programs of any substantial size or complexity. Code generated by the Codex compiler has no guarantee of functionality, and code produced by the Codex compiler may occasionally contain incorrect or harmful content.

Codex is a programming language with minimal syntax where the behavior of the program is not explicitly defined. Instead, the behavior of Codex programs are described using plain English, and the actual implementation of the code is filled in by [OpenAI Codex](https://openai.com/blog/openai-codex/), a generative model designed to produce code from natural language descriptions.

The Codex compiler takes a program and uses OpenAI Codex to implement it, outputting the source code for a standalone program in any one of the following languages:
 - Python
 - Java (not yet supported)
 - Javascript (not yet supported)
 - Typescript (not yet supported)

Below is an example of a Codex program that adds two numbers.
```rust
fn add(int a, int b) -> int: return the sum of a and b

fn main() >
    var int a: a random number from 1 to 10
    var int b: a random number from 1 to 10

    ![add]: add a and b, and print the result
```