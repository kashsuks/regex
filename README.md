# Regecks
 A regex engine built from scratch using python, and a TUI using Textual!

 Ever part of this including stuff like the lexer, parser, the ast, and the backtracking were written by hand :)

 ## Installation

 Requires [uv](https://docs.astral.sh/uv/)

 ```bash
git clone https://github.com/kashsuks/regecks
cd regecks
uv sync
 ```
## Running

```bash
uv run regecks
```

## Keybindings

| **Key** | **Action**                                  |
|---------|---------------------------------------------|
| Tab     | Move between pattern and test string fields |
| Ctrl+R  | Run match manually                          |
| Ctrl+C  | Quit                                        |

Matches get updated live

## Supported Syntax

### Literals

| Pattern | Match                  |
|---------|------------------------|
| a       | The character a        |
| abc     | The string abc exactly |

### Wildcard

| Pattern | Match                               |
|---------|-------------------------------------|
| .       | Any single character except newline |

### Quantifiers

All quantifiers are greedy and therefore consume as much as possible.

| Pattern | Match                         |
|---------|-------------------------------|
| a*      | Zero or more a                |
| a+      | One or more a                 |
| a?      | Zero or one a                 |
| a{3}    | Exactly 3 a                   |
| a{2,}   | 2 or more a                   |
| a{2,4}  | Between 2 and 4 a (inclusive) |

### Anchors

| Pattern | Match                               |
|---------|-------------------------------------|
| ^abc    | abc only at the start of the string |
| abc$    | abc only at the end of the string   |
| \b      | Word boundary (between \w and \W)   |
| \B      | Non-word boundary                   |

### Character classes

| Pattern  | Match                         |
|----------|-------------------------------|
| [abc]    | Any one of a, b, or c         |
| [a-z]    | Any lowercase letter          |
| [A-Z0-9] | Any uppercase letter or digit |
| [^abc]   | Any character except a, b, c  |
| [^0-9]   | Any non-digit                 |

### Escape sequences

| Pattern | Match                                     |
|---------|-------------------------------------------|
| \d      | Any digit [0-9]                           |
| \D      | Any non-digit                             |
| \w      | Any word character [a-zA-Z0-9_]           |
| \W      | Any non-word character                    |
| \s      | Any whitespace (space, tab, newline, etc) |
| \S      | Any non-whitespace                        |
| \n      | Newline                                   |
| \t      | Tab                                       |
| \n      | Literal dot (escaping special chars)      |

### Alternation

| Pattern       | Match             |
|---------------|-------------------|
| cat\|dog      | Either cat or dog |
| foo\|bar\|baz | Any of the three  |

### Groups

| Pattern       | Match                                  |
|---------------|----------------------------------------|
| (abc)         | abc, captured as group 1               |
| (a)(b)        | ab, with a as group 1 and b as group 2 |
| (?:abc)       | abc, not captured                      |
| (?P<name>abc) | abc, captured as named group name      |

### Flags

| Pattern | Match                                                   |
|---------|---------------------------------------------------------|
| (?iabc) | Match abc case-insensitively and matches ABC, abc, etc. |

The flags wrap everything that follows it in a pattern

### Lookahead and lookbehind

These are zero-width assertions meaning they check for a condition without consuming characters.
