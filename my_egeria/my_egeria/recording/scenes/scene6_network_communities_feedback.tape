# VHS Tape: Scene 6 - Collaboration, Networks & Technology Curation
Output scene6_network_communities_feedback.mp4
Output scene6_network_communities_feedback.gif

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

# Scene 6: Collaboration, Networks & Feedback (Target Duration: ~38s)
Type "uv run my_profile"
Sleep 500ms
Enter
Sleep 3s

# Immediately enter Main Dashboard (0s-4s)
Enter
Sleep 1.5s

# 4s-13s: "My Profile also strengthens our human network... My Network visualizes collaboration graphs..."
Tab 2
Down 1
Sleep 1s
Enter
Sleep 2s
Screenshot scene6_my_network_graph.png
Sleep 5s
Escape
Sleep 1s

# 13s-22s: "Work with Communities connects us to cross-functional working groups..."
Down 1
Sleep 1s
Enter
Sleep 2s
Screenshot scene6_communities_screen.png
Sleep 4.5s
Escape
Sleep 1s

# 22s-29s: "If I notice something that needs improvement, pressing Control plus F lets me log feedback..."
Ctrl+F
Sleep 1.5s
Screenshot scene6_leave_feedback_modal.png
Type "Great catalog navigation! Requesting automated lineage graph view."
Sleep 3s
Escape
Sleep 1s

# 29s-38s: "And for our integration architects like Bob Nitter, the Technology Types screen displays..."
Down 3
Sleep 1s
Enter
Sleep 2s
Screenshot scene6_technology_types.png
Sleep 6s
