# Reference

Despite the existence of GitPython, it remains awkward to access structured diffs for a given repo.
This is particularly desirable for large diff sets, such as those created when migrating between
linters (such as Black to Ruff, as motivated this library). In such cases it's desirable to be able
to see clearly what the actual substance of the set of diffs is, but without programmatic means to
access this set simply it becomes a manual effort (with each reader re-duplicating others' efforts
or else just skipping the task and not making an informed decision).

Before writing this library I investigated fast parsing approaches (Pydantic with Rust's regex
crate in particular) and reviewed the internals of GitPython, as well as its API for accessing diffs.

The goal of this library is to make this specific facet of git easy to work with.
