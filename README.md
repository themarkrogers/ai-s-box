# AI S-Box

## Installation

This project requires Python3.12.


## Introduction

The goal of this project is to use an LLM to generate a few cryptographically secure S-Boxes.

Specifically, I want to generate S-Boxes that fit these criteria:
* Input Length: 3, Output Length: 3, Num Symbols: 125 (5^3)
* Input Length: 3, Output Length: 3, Num Symbols: 216 (6^3)
* Input Length: 3, Output Length: 3, Num Symbols: 343 (7^3)
* Input Length: 3, Output Length: 3, Num Symbols: 512 (8^3)
* Input Length: 3, Output Length: 3, Num Symbols: 729 (9^3)
* Input Length: 3, Output Length: 3, Num Symbols: 1000 (10^3)
* Input Length: 3, Output Length: 3, Num Symbols: 1331 (11^3)

Bonus Points if I can also generate s-boxes for these criteria
* Input Length: 3, Output Length: 3, Num Symbols: 150 (5x5x6)
* Input Length: 3, Output Length: 3, Num Symbols: 175 (5x5x8)
* Input Length: 3, Output Length: 3, Num Symbols: 180 (5x6x6)
* Input Length: 3, Output Length: 3, Num Symbols: 210 (5x6x7)
* Input Length: 3, Output Length: 3, Num Symbols: 225 (5x6x9)
* Input Length: 3, Output Length: 3, Num Symbols: 250 (5x5x10)
* Input Length: 3, Output Length: 3, Num Symbols: 252 (6x6x7)
* Input Length: 3, Output Length: 3, Num Symbols: 275 (5x5x11)
* Input Length: 3, Output Length: 3, Num Symbols: 294 (6x7x7)


## Strategy

Make a dspy.Signature that takes in English and outputs python3 code
* Ensure that the output of the generated python3 code is always a list[list[str]]

Make a dspy.Module that leverages that Signature
* Use the validate_s_box function to assign a score
* Use the known-good s-boxes as Few Shot examples to seed the AI Program
* Iterate until a few candidate s-boxes are generated
* Write those to disk (as we validate each one)


## Resources

Useful cryptography links:
* https://en.wikipedia.org/wiki/S-box
* https://en.wikipedia.org/wiki/Rijndael_S-box
* https://en.wikipedia.org/wiki/DES_supplementary_material

Useful AI links:
* [DSPy tutorial 1](https://www.youtube.com/watch?v=41EfOY0Ldkc)
* [DSPy tutorial 2](https://www.youtube.com/watch?v=_ROckQHGHsU)
* [TextGrad tutorial](https://www.youtube.com/watch?v=Qks4UEsRwl0)
