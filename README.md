# Codex

Codex is a concept programing language powered by the OpenAI generative model of the same name.

## Introduction

> **Warning:** Codex is a heavily experimental concept language, and it is not intended for production use. See the disclaimer section below for more information.

Codex is a programming language with minimal syntax where the behavior of the program is not explicitly defined. Instead, the behavior of Codex programs are described using plain English, and the actual implementation of the code is filled in by [OpenAI Codex](https://openai.com/blog/openai-codex/), a generative model designed to produce code from natural language descriptions.

The Codex compiler takes a program and uses OpenAI Codex to implement it, outputting the source code for a standalone program in any one of the following languages:

-   Python
-   Typescript
-   Java (not yet supported)
-   Javascript (not yet supported)

Below is an example of Hello World in Codex:

```rust
!: print hello world
```

The `!:` syntax is analogous to a regular code comment whose content will correspond to AI-generated code.

For example, here is an example of a program that prints the first 10 Fibonacci numbers:

```rust
var array fibs: the first 10 fibonacci numbers

!: print fibs
```

We can also write the output to a file:

```rust
using fs

var array fibs: the first 10 fibonacci numbers

!: write fibs to fibs.txt as a comma-separated list
```

The `using` keyword is used to import Codex standard library modules. In this example, the `fs` provides filesystem access. The exact behavior of the `using` directive depends on the target language, but in general, it will import the corresponding standard library module.

Even though the output of the Codex compiler is largely AI-generated, the `using` directive helps to ensure that the output is valid code.

## Getting Started

1. In order to use Codex, you will need to [sign up for an OpenAI API key](https://platform.openai.com/account/api-keys). As of writing, the OpenAI code generation endpoint used by the compiler is free to use, but you still may need to provide a payment method to sign up for an API key. Once you have obtained an API key,
2. Install dependencies using `pip install -r requirements.txt`.
3. Run the Codex compiler using `python -m codex [input-file]`. Use `python -m codex --help` for more information.

## Installation

Codex can also be installed to `/usr/local/bin` on Unix systems using `python3 install.py`. Keep in mind that this will overwrite any existing Codex installation, and the executable will be linked to wherever this repository is located on your system. This script will not automatically install dependencies, so you will need to run `pip install -r requirements.txt` before running the installation script.

## Disclaimer and Terms of Use

Codex is not indented for production use or for writing programs of any substantial size or complexity. Code generated by the Codex compiler has no guarantee of functionality, and code produced by the Codex compiler may occasionally contain incorrect or harmful content.

Codex source code must adhere to the [OpenAI Usage Policies](https://platform.openai.com/docs/usage-policies).

Code produced by the Codex compiler may occasionally produce code with security vulnerabilities ([Pearce, et al.](https://arxiv.org/abs/2108.09293)). Use of the Codex compiler is at your own risk.
