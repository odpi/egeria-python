# VHS Tape: Scene 2 - Launch & Background Startup
Output scene2_launch_and_startup.mp4
Output scene2_launch_and_startup.gif

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

# Scene 2: Launch & Parallel Background Startup (Target Duration: ~33s)
# 0s-3s: Launch command
Type "uv run my_profile"
Sleep 500ms
Enter
Sleep 3.5s

# 3s-13s: Highlight Welcome Splash Screen & Background Querying
Screenshot scene2_splash_welcome.png
Sleep 6s

# 13s-22s: "By the time you hit Continue, your full profile is loaded..."
Enter
Sleep 4s
Screenshot scene2_main_loaded.png
Sleep 4s

# 22s-33s: "And if I'm pairing with Peter Profile... Change User lets us switch..."
# Highlight loaded Main Dashboard with User Associations & Collections
Tab
Sleep 2s
Down 1
Sleep 2s
Up 1
Sleep 5s
