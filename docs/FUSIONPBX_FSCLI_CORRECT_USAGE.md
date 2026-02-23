# FreeSWITCH CLI (fs_cli) Correct Usage

## Important: Two Ways to Use fs_cli

### Method 1: Command Line (One-liner)
Use `-x` flag from your shell/terminal:

```bash
# From command line (NOT inside fs_cli)
fs_cli -x "sofia status profile internal"
fs_cli -x "reloadxml"
fs_cli -x "show dialplan"
```

### Method 2: Interactive Mode
Enter fs_cli, then type commands WITHOUT `-x`:

```bash
# Enter interactive mode
fs_cli

# Then type commands (NO -x, NO quotes)
freeswitch@fusionpbx2> sofia status profile internal
freeswitch@fusionpbx2> reloadxml
freeswitch@fusionpbx2> show dialplan

# Exit interactive mode
freeswitch@fusionpbx2> /bye
# Or press Ctrl+D
```

## Common Commands for Dialplan Debugging

### From Command Line:
```bash
# Check SIP profile context
fs_cli -x "sofia status profile internal"

# Reload XML
fs_cli -x "reloadxml"

# Show all dialplan types
fs_cli -x "show dialplan"

# Check if extension is registered
fs_cli -x "sofia status" | grep 2001
```

### Inside fs_cli (Interactive):
```bash
fs_cli
# Then:
sofia status profile internal
reloadxml
show dialplan
sofia status
/bye
```

## Your Current Task

To check the SIP profile context, you have two options:

**Option A: From command line**
```bash
# Exit fs_cli first (type /bye or Ctrl+D)
root@fusionpbx2:~# fs_cli -x "sofia status profile internal"
```

**Option B: Inside fs_cli**
```bash
freeswitch@fusionpbx2> sofia status profile internal
```

Both will show the same information, including the `Context` setting.

