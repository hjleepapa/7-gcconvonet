# FusionPBX Dialplan Action Options for Transfer

## Problem
The "transfer" action is not in the dropdown menu. You need to type it manually or use an alternative action.

## Solution Options

### Option 1: Type "transfer" Manually (Recommended)

**Action 1:**
- Click in the Action 1 field
- **Type manually**: `transfer` (don't select from dropdown)
- **Value field**: `2001 XML internal`
- Click the blue arrow button (←) to add

**Format:**
```
Action: transfer
Value: 2001 XML internal
```

This tells FusionPBX to transfer the call to extension 2001 in the internal context using XML dialplan.

### Option 2: Use "bridge" Action

If "transfer" doesn't work, try "bridge":

**Action 1:**
- Click in the Action 1 field
- **Type manually**: `bridge`
- **Value field**: `user/2001@internal`
- Click the blue arrow button (←) to add

**Format:**
```
Action: bridge
Value: user/2001@internal
```

### Option 3: Use "set" + "transfer" (Advanced)

If neither works, you might need two actions:

**Action 1:**
- Type: `set`
- Value: `transfer_after_bridge=true`

**Action 2:**
- Type: `transfer`
- Value: `2001 XML internal`

## Complete Configuration

Based on your interface:

1. **Name:** `Twilio-to-Extension-2001`

2. **Condition 1:**
   - Field: `destination_number`
   - Operator: `=`
   - Value: `2001`
   - Click arrow (←)

3. **Action 1:**
   - **Type manually**: `transfer`
   - Value: `2001 XML internal`
   - Click arrow (←)

4. **Context:** `public`

5. **Order:** `100`

6. **Enabled:** `True`

7. **Description:** `Route Twilio SIP calls to extension 2001`

## Testing

After saving, test with:
```bash
# On FusionPBX server - CORRECT COMMAND
fs_cli -x "xml_locate dialplan public 2001"

# Or interactive mode:
fs_cli
# Then type: xml_locate dialplan public 2001

# Or check all dialplans:
fs_cli -x "show dialplan public"
```

Should show XML with transfer application.

**Note:** The command `dialplan xml` doesn't exist. Use `xml_locate dialplan` instead.

## Alternative: Use Dialplan XML Directly

If the GUI doesn't work, you can edit the dialplan XML directly:

1. SSH to FusionPBX server
2. Edit: `/etc/freeswitch/dialplan/public.xml` (or wherever your public context is)
3. Add:
   ```xml
   <extension name="Twilio-to-Extensions">
     <condition field="destination_number" expression="^2001$">
       <action application="transfer" data="2001 XML internal"/>
     </condition>
   </extension>
   ```
4. Reload: `fs_cli -x "reloadxml"`

## Troubleshooting

**If "transfer" doesn't work:**
- Try `bridge` with `user/2001@internal`
- Try `bridge` with `sofia/internal/2001@internal`
- Check FusionPBX logs for errors

**If extension not found:**
- Verify extension 2001 exists: `fs_cli -x "user_data 2001@internal var"`
- Check extension is registered: `fs_cli -x "sofia status"`

