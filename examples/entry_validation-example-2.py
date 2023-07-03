# https://stackoverflow.com/a/56617051
# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry-validation.html


import tkinter as tk


def validator(P):
    """Validates the input.

    Args:
        P (int): the value the text would have after the change.

    Returns:
        bool: True if the input is digit-only or empty, and False otherwise.
    """

    return P.isdigit() or P == ""


root = tk.Tk()

entry = tk.Entry(root)
entry.configure(
    validate="key",
    validatecommand=(
        root.register(validator),
        "%P",
    ),
)
entry.grid()

root.mainloop()