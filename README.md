# Interpreters and Compilers

### What is this?

I started playing with interpreters/compilers reading Thorsten Ball's excellent [books](https://thorstenball.com/#books)–highly recommend these! They've provided me with a good introduction and appreciation for how interpreters/compilers work and a hunger to probe deeper into various languages. In this repo, I plan to document my tinkering/understanding
languages by building interpreters and/or compilers for various languages such as Lisp.

### But, why?

Because it's fun!

But on a more practical level, understanding how interpreters/compilers work is very useful. I recommending reading 
[Steve Yegge](http://steve-yegge.blogspot.com/2007/06/rich-programmer-food.html)'s article where he gives some examples of when they can be used. He also says the following: 

> "If you don't know how compilers work, then you don't know how computers work." 

You can probably get by without the knowledge of compilers. But not understanding how languages work can make it seem like they are pure magic–really, they are just interfaces to make it easier to work with the computer. Even if you use advanced tools like [ANTLR](https://www.antlr.org) or simpler ones like [lark](https://github.com/lark-parser/lark), this knowledge can help you understand how these tools work under the hood when things go awry.

### Goals

I have two main goals:

- Documenting my exploration with languages with code (and comments within)
- Writing posts to help myself and others understand the process of lexing, parsing, interpreting/compiling, and evaluating code.

For some of these, I won't be building from scratch and instead following, documenting and adding to existing guides. This approach is nice for getting bootstrapped into the process so it's easier to augment the language with optimizations or human-friendly error messages etc.

However for others, I will be writing from scratch, especially when I want to build a new language. This approach is more involved but provides absolute control and is more satisfying for having built everything yourself.

