import tkinter as tk

class ToolTip:
    """
    Create a tooltip for a given widget.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip) # 延迟500ms显示

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "9", "normal"), wraplength=250)
        label.pack(ipadx=4, ipady=2)

    def hidetip(self):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

class ComboboxSearch:
    """
    Adds search-as-you-type functionality to a ttk.Combobox.
    """
    def __init__(self, combobox, timeout=1000):
        self.combobox = combobox
        self.timeout = timeout
        self.search_term = ""
        self.after_id = None
        self.combobox.bind('<KeyRelease>', self.on_key_release)

    def on_key_release(self, event):
        """Handles the key release event."""
        if self.after_id:
            self.combobox.after_cancel(self.after_id)

        if event.keysym == 'BackSpace':
            self.search_term = self.search_term[:-1]
        elif event.char and event.char.isprintable():
            self.search_term += event.char.lower()
        else:
            # Ignore non-printable keys like Shift, Control, etc.
            return

        self.after_id = self.combobox.after(self.timeout, self.reset_search)
        self.perform_search()

    def perform_search(self):
        """Searches for the term in the combobox values and selects the first match."""
        values = self.combobox['values']
        for i, value in enumerate(values):
            if str(value).lower().startswith(self.search_term):
                self.combobox.current(i)
                self.combobox.event_generate("<<ComboboxSelected>>")
                break

    def reset_search(self):
        """Resets the search term after a timeout."""
        self.search_term = ""
        self.after_id = None