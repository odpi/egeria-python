# VHS Tape: Scene 4 - Real-Time Curation: To-Dos, Comments & Bookmarks
Output scene4_curation_todos_comments.mp4
Output scene4_curation_todos_comments.gif

Set Shell "bash"
Set FontSize 18
Set FontFamily "Menlo"
Set Width 1920
Set Height 1080
Set Padding 20
Set Theme "Catppuccin Mocha"
Set WindowBar "Colorful"
Set WindowBarSize 40
Set MarginFill "#1e1e2e"
Set BorderRadius 10
Set TypingSpeed 50ms

Type "unset NO_COLOR && export COLORTERM=truecolor TERM=xterm-256color FORCE_COLOR=1 && clear"
Enter
Sleep 500ms

# Scene 4: Real-Time Curation: To-Dos, Comments & Bookmarks (Target Duration: ~41s)
Type "uv run my_profile"
Sleep 500ms
Enter
Sleep 3s

# Immediately enter Main Dashboard (0s-4s)
Enter
Sleep 1.5s

# 4s-14s: "Data governance only works if metadata is maintained... Pressing Control plus T lets me edit any highlighted table in place..."
Tab 3
Sleep 1s
Down 2
Sleep 1s
Ctrl+T
Sleep 1.5s
Screenshot scene4_edit_todos_dialog.png
Tab
Sleep 500ms
Type "Verify hospital cohort schema with Peter Profile"
Sleep 3s
Escape
Sleep 1s

# 14s-29s: "With Control plus O and Control plus N, threaded discussions attach directly to the metadata asset or task itself..."
# Open View Comments (Ctrl+O)
Ctrl+O
Sleep 2s
Screenshot scene4_view_comments.png
Sleep 4s
Escape
Sleep 1s

# Open Add Comment (Ctrl+N)
Ctrl+N
Sleep 1.5s
Screenshot scene4_add_comment_modal.png
Type "Confidence score 0.95 verified against clinical laboratory assay standards"
Sleep 3.5s
Escape
Sleep 1s

# 29s-41s: "And with Control plus K and Control plus B, I can bookmark key assets and retrieve them instantly..."
Ctrl+K
Sleep 1.5s
Ctrl+B
Sleep 2s
Screenshot scene4_my_bookmarks_screen.png
Sleep 7s
