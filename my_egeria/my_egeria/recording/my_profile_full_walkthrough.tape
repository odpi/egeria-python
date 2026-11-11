# VHS Tape: My Profile - Full Walkthrough
# Reproduces the complete video script sequence (Scenes 2 to 6) for Callie Quartile
# Output: mp4 and gif recordings

Output my_profile_full_walkthrough.mp4
# Output my_profile_full_walkthrough.gif

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

# Configure 24-bit TrueColor terminal environment
Type "unset NO_COLOR && export COLORTERM=truecolor TERM=xterm-256color FORCE_COLOR=1 && clear"
Enter
Sleep 500ms

# ==============================================================================
# Scene 2: Launch & Parallel Background Startup (0s to 33.7s)
# ==============================================================================
# 0s-3s: Launch command
Type "uv run my_profile"
Sleep 500ms
Enter
Sleep 3.5s

# 3.5s-14s: Welcome Splash Screen displays with async loading
Screenshot splash_screen.png
Sleep 10.5s

# 14s-21s: Continue into Main Dashboard
Enter
Sleep 3s
Screenshot main_dashboard.png
Sleep 3.5s

# 21s-33.7s: Highlight loaded profile, User Associations & Collections
Tab
Sleep 2.5s
Down 1
Sleep 3s
Up 1
Sleep 3s
Sleep 3.7s

# ==============================================================================
# Scene 3: Main Dashboard Tour (33.7s to 77.5s)
# ==============================================================================
# 33.7s-45s: Explore User Associations & Collections
Tab
Sleep 2.5s
Down 1
Sleep 3s
Up 1
Sleep 4.5s

# 45s-61.5s: Roles & Teams drill-down -> Open My Team screen
Tab
Sleep 1.5s
Enter
Sleep 2s
Screenshot my_team.png
Sleep 10s
Escape
Sleep 1.5s

# 61.5s-69s: Activity Stream (Blogs, Journal, To-Dos)
Tab
Sleep 1.5s
Down 2
Sleep 5.5s

# 69s-77.5s: Karma Points recognition
Up 2
Sleep 2s
Shift+Tab
Shift+Tab
Sleep 6.5s

# ==============================================================================
# Scene 4: Real-Time Curation: To-Dos, Comments & Bookmarks (77.5s to 118.3s)
# ==============================================================================
# 77.5s-91s: Edit Table (Ctrl+T) on To-Dos
Tab 3
Sleep 1s
Down 2
Sleep 1.5s
Ctrl+T
Sleep 1.5s
Screenshot edit_todos.png
Tab
Sleep 500ms
Type "Verify hospital cohort schema with Peter Profile"
Sleep 3s
Escape
Sleep 1.5s

# 91s-97s: View Comments (Ctrl+O)
Ctrl+O
Sleep 2.5s
Screenshot show_comments.png
Escape
Sleep 1.5s

# 97s-107.5s: Add Comment (Ctrl+N)
Ctrl+N
Sleep 1.5s
Screenshot add_comment.png
Type "Confidence score 0.95 verified against clinical laboratory assay standards"
Sleep 3.5s
Escape
Sleep 2s

# 107.5s-118.3s: Bookmark Row (Ctrl+K) & View Bookmarks (Ctrl+B)
Ctrl+K
Sleep 1.5s
Ctrl+B
Sleep 2s
Screenshot my_bookmarks.png
Sleep 5s
Escape
Sleep 1.3s

# ==============================================================================
# Scene 5: Hero Workflow: Shopping for Governed Data Products (118.3s to 174.7s)
# ==============================================================================
# 118.3s-138s: Open Shop for Data & Browse Catalogs
Tab 2
Down 6
Sleep 1s
Enter
Sleep 3s
Screenshot shop_for_data.png
Tab
Sleep 2s
Down 2
Sleep 3.5s
Down 1
Sleep 6.5s

# 138s-149.5s: Sample Data Modal (Ctrl+L)
Ctrl+L
Sleep 2s
Screenshot sample_data.png
Sleep 7.5s
Escape
Sleep 1.5s

# 149.5s-164.5s: Create Subscription Request (Ctrl+U)
Ctrl+U
Sleep 2s
Screenshot create_subscription.png
Tab
Sleep 500ms
Type "AI oncology treatment response modeling"
Sleep 3.5s
Escape
Sleep 1.5s

# 164.5s-174.7s: Return to Main Dashboard and View Subscriptions
Escape
Sleep 1.5s
Tab 2
Down 5
Sleep 1s
Enter
Sleep 2s
Screenshot subscriptions.png
Sleep 4s
Escape
Sleep 0.7s

# ==============================================================================
# Scene 6: Collaboration, Networks & Technology Curation (174.7s to 212.0s)
# ==============================================================================
# 174.7s-185s: My Network Graph Visualization
Tab 2
Down 1
Sleep 1s
Enter
Sleep 2s
Screenshot my_network.png
Sleep 5s
Escape
Sleep 1s

# 185s-193.5s: Work with Communities
Down 1
Sleep 1s
Enter
Sleep 2s
Screenshot communities.png
Sleep 3.5s
Escape
Sleep 1s

# 193.5s-202.5s: In-App Feedback Dialog (Ctrl+F)
Ctrl+F
Sleep 1.5s
Screenshot leave_feedback.png
Type "Great catalog navigation! Requesting automated lineage graph view."
Sleep 2.5s
Escape
Sleep 1.5s

# 202.5s-212s: Technology Types Screen
Down 3
Sleep 1s
Enter
Sleep 2s
Screenshot tech_types.png
Sleep 5.5s
