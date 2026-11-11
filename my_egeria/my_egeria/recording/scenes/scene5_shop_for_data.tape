# VHS Tape: Scene 5 - Hero Workflow: Shopping for Governed Data Products
Output scene5_shop_for_data.mp4
Output scene5_shop_for_data.gif

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

# Scene 5: Hero Workflow: Shopping for Governed Data Products (Target Duration: ~56s)
Type "uv run my_profile"
Sleep 500ms
Enter
Sleep 3s

# Immediately enter Main Dashboard (0s-4s)
Enter
Sleep 1.5s

# 4s-20s: "Now for the most powerful feature in my workflow: Shop for Data... Egeria brings together Business Domains, Glossaries, Data Dictionaries..."
Tab 2
Down 6
Sleep 1s
Enter
Sleep 3s
Screenshot scene5_shop_for_data_overview.png
Tab
Sleep 1.5s
Down 2
Sleep 2s
Screenshot scene5_catalog_selection.png
Sleep 4s

# 20s-34s: "I can explore standardized terminology, verify classifications, and hit Control plus L to sample the dataset right in my terminal..."
Ctrl+L
Sleep 2s
Screenshot scene5_sample_data_modal.png
Sleep 9s
Escape
Sleep 1.5s

# 34s-45s: "When it's right, Control plus U lets me submit a formal Subscription Request..."
Ctrl+U
Sleep 2s
Screenshot scene5_subscription_request_modal.png
Tab
Sleep 500ms
Type "AI oncology treatment response modeling"
Sleep 4s
Escape
Sleep 1.5s

# 45s-56s: "In less than sixty seconds, governed access is requested, validated, and tracked in Subscriptions."
Escape
Sleep 1.5s
Tab 2
Down 5
Sleep 1s
Enter
Sleep 2s
Screenshot scene5_active_subscriptions.png
Sleep 6s
