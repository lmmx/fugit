# Reference

Accessing structured diffs in a Git repository remains challenging, even with tools like GitPython.
This issue is especially pronounced when dealing with large diff sets, such as those generated
during transitions between linters (e.g., from Black to Ruff). Currently, without a straightforward
programmatic solution, understanding the essence of these diffs requires cumbersome manual effort.

Before writing this library I explored fast parsing approaches (Pydantic's integration with Rust's regex
crate in particular) and reviewed GitPython internals, as well as its pitfalls.

_fugit_ simplifies access to git diffs, and will help you avoid the covert hazards in GitPython's API.
