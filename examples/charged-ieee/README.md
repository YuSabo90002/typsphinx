# charged-ieee Template Example

This example demonstrates two approaches for using the charged-ieee Typst Universe template with sphinx-typst.

## Overview

The [charged-ieee](https://typst.app/universe/package/charged-ieee/) template from Typst Universe provides IEEE-style formatting for academic papers. This example shows how to use it with sphinx-typst in two different ways.

## Approach 1: Configuration-Based (Recommended)

**Location**: `approach1/`

**Pros**:
- Simple and concise
- All configuration in `conf.py`
- No Typst code required
- Easy to maintain

**Cons**:
- Less flexible for complex transformations
- Limited to what the configuration options support

**Use when**:
- Standard template usage is sufficient
- You want minimal configuration
- You don't need complex author information transformations

### Configuration Example

```python
# Author details with dictionary format
typst_authors = {
    "John Doe": {
        "department": "Computer Science",
        "organization": "MIT",
        "email": "john.doe@mit.edu"
    }
}

# Template function with parameters
typst_template_function = {
    "name": "ieee",
    "params": {
        "abstract": ieee_abstract,
        "index-terms": ieee_keywords,
        "paper-size": "a4",
    }
}
```

## Approach 2: Custom Template (Flexible)

**Location**: `approach2/`

**Pros**:
- Full flexibility with Typst code
- Can implement complex transformations
- Complete control over template behavior
- Can add custom styling and logic

**Cons**:
- Requires Typst knowledge
- More code to maintain
- Slightly more complex setup

**Use when**:
- You need complex author transformations
- You want custom styling or behavior
- Configuration-based approach is too limiting
- You're comfortable writing Typst code

### Custom Template Example

```typst
#import "@preview/charged-ieee:0.1.4": ieee

#let project(title: "", authors: (), body) = {
  // Transform author strings to IEEE format
  let ieee_authors = authors.map(name => (
    name: name,
    department: "Computer Science",
    organization: "MIT",
  ))

  show: ieee.with(
    title: title,
    authors: ieee_authors,
    abstract: [...],
    index-terms: ("AI", "ML"),
  )

  body
}
```

## Building the Examples

### Approach 1

```bash
cd approach1
sphinx-build -b typst -c . source build/typst
cd build/typst
typst compile paper.typ output.pdf
```

### Approach 2

```bash
cd approach2
sphinx-build -b typst -c . source build/typst
cd build/typst
typst compile paper.typ output.pdf
```

## Comparison

| Feature | Approach 1 | Approach 2 |
|---------|-----------|-----------|
| Setup Complexity | ✅ Simple | ⚠️ Moderate |
| Flexibility | ⚠️ Limited | ✅ Full |
| Typst Knowledge Required | ❌ No | ✅ Yes |
| Maintenance | ✅ Easy | ⚠️ Moderate |
| Custom Transformations | ❌ No | ✅ Yes |
| Recommended For | Most users | Advanced users |

## When to Choose Which Approach

### Choose Approach 1 if:
- You're new to Typst
- You want the simplest setup
- Standard template features are sufficient
- You prefer configuration over code

### Choose Approach 2 if:
- You need custom author transformations
- You want to add custom styling
- You need complex parameter calculations
- You're comfortable with Typst syntax

## Additional Resources

- [charged-ieee on Typst Universe](https://typst.app/universe/package/charged-ieee/)
- [Typst Documentation](https://typst.app/docs)
- [sphinx-typst Documentation](https://github.com/YuSabo90002/typsphinx)

## Notes

- Both approaches produce identical output when configured correctly
- Approach 1 is recommended for most use cases
- Approach 2 provides an escape hatch for complex requirements
- `typst_authors` (the author-details configuration) can be combined with the
  custom-template route in Approach 2 — but `typst_package` and `typst_template`
  are mutually exclusive and cannot be set together
