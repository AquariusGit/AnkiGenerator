import tkinter as tk
from anki_generator import AnkiGeneratorApp
from helper import Start

def main():
    """
    Main function to initialize and run the Anki Generator application.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window initially

    # Run the initial setup check. This might show a setup dialog.
    start_instance = Start(root)

    # Proceed only if the initial setup was completed or not needed.
    if start_instance.should_continue:
        root.deiconify()  # Show the main window
        app = AnkiGeneratorApp(root)
        root.mainloop()
    else:
        # If setup was cancelled, the program can just exit.
        root.destroy()

if __name__ == "__main__":
    main()