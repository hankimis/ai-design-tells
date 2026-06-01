# vhs tape — records the AI Design Tells harness running in a real terminal.
# Run from the project root:  vhs tape/demo.tape
Output paper/figs/gif_terminal.gif

Set Shell zsh
Set FontSize 16
Set Width 1180
Set Height 840
Set Padding 24
Set Theme "Tomorrow Night"

Sleep 600ms
Type "# Score a corpus of pages for AI design tells (lower is better)"
Enter
Sleep 500ms
Type "python3 src/cli.py fixtures/*.html --quiet"
Enter
Sleep 4s

Type "# Audit a designed page — does it read as intentional?"
Enter
Sleep 400ms
Type "python3 src/cli.py fixtures/refined.html"
Enter
Sleep 3500ms
