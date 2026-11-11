# VHS Tape: Scene 3 - Main Dashboard Tour
Output scene3_main_dashboard.mp4
Output scene3_main_dashboard.gif

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

# Scene 3: Main Dashboard Tour (Target Duration: ~44s)
Type "uv run my_profile"
Sleep 500ms
Enter
Sleep 3s

# Immediately continue into Main Dashboard (0s-4s)
Enter
Sleep 2s

# 4s-13s: "Here is my daily home base... At the top, my User Associations and Collections..."
Screenshot scene3_dashboard_overview.png
Tab
Sleep 2s
Down 1
Sleep 2s
Up 1
Sleep 3s

# 13s-28s: "In the middle, you see my appointed Roles and Teams... pressing Enter on my Clinical Trials team role opens My Team..."
Tab
Sleep 1.5s
Screenshot scene3_roles_panel.png
Sleep 1.5s
Enter
Sleep 2s
Screenshot scene3_my_team_drilldown.png
Sleep 8s
Escape
Sleep 1.5s

# 28s-36s: "Down here is my daily activity stream: team Blogs, my personal Journal, and my To-Dos..."
Tab
Sleep 1.5s
Down 2
Sleep 2s
Screenshot scene3_activities.png
Sleep 4.5s

# 36s-44s: "And at the top right, Egeria tracks my Karma Points, recognizing active curation..."
Up 2
Sleep 2s
Shift+Tab
Shift+Tab
Sleep 4s
