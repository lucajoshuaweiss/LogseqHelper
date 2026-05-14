"""
Mouse wheel binding utilities.
"""


def on_mousewheel(event, canvas):
    if event.delta:
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    else:
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")


def bind_mousewheel(widget, callback):
    widget.bind("<MouseWheel>", callback)
    widget.bind("<Button-4>", callback)
    widget.bind("<Button-5>", callback)

    for child in widget.winfo_children():
        bind_mousewheel(child, callback)


def unbind_mousewheel(widget):
    widget.unbind_all("<MouseWheel>")
    widget.unbind_all("<Button-4>")
    widget.unbind_all("<Button-5>")