# FusionPBX Dialplan Quick Setup Guide

## Step-by-Step Configuration

Based on the FusionPBX dialplan manager interface you're seeing:

### Configuration Values

1. **Name:**
   ```
   Twilio-to-Extension-2001
   ```

2. **Context:**
   ```
   public
   ```
   ⚠️ **IMPORTANT**: Change from `10.128.0.10` to `public`

3. **Condition 1:**
   - Click in the Condition 1 field
   - Type or select: `destination_number`
   - In the dropdown, select: `=` (equals)
   - In the value field: `2001`
   - Click the blue arrow button (←) to add the condition

4. **Action 1:**
   - Click in the Action 1 field
   - **Type manually**: `transfer` (it's not in the dropdown, you need to type it)
   - In the value field: `2001 XML internal`
   - Click the blue arrow button (←) to add the action
   - *Alternative: Try `bridge` with value `user/2001@internal` if transfer doesn't work*

5. **Order:**
   ```
   100
   ```
   (Lower numbers = higher priority)

6. **Enabled:**
   ```
   True
   ```
   (Keep as is)

7. **Description:**
   ```
   Route Twilio SIP calls to extension 2001
   ```
   (Optional but helpful)

### Visual Guide

```
┌─────────────────────────────────────────┐
│ Name: Twilio-to-Extension-2001          │
├─────────────────────────────────────────┤
│ Condition 1: destination_number = 2001  │ [←]
├─────────────────────────────────────────┤
│ Action 1: transfer = 2001@internal      │ [←]
├─────────────────────────────────────────┤
│ Context: public                          │
│ Order: 100                               │
│ Enabled: True                            │
│ Description: Route Twilio SIP calls...   │
└─────────────────────────────────────────┘
```

### What This Does

When Twilio sends a SIP call to `sip:2001@136.115.41.45`:
1. FusionPBX receives it in the `public` context
2. Condition matches: `destination_number = 2001`
3. Action executes: `transfer 2001@internal`
4. Call is routed to extension 2001 in the internal context

### For All Extensions (Advanced)

If you want to route ANY extension number dynamically:

**Condition 1:**
- Field: `destination_number`
- Operator: `=~` (regex match) or use `destination_number` with regex
- Value: `^(\d+)$`

**Action 1:**
- Field: `transfer`
- Value: `${destination_number}@internal`

This will route `2001`, `2002`, `2003`, etc. automatically.

### Testing

After saving, test with:
```bash
# On FusionPBX server
fs_cli -x "dialplan xml public 2001"
```

Should show XML with transfer to `2001@internal`.

### Troubleshooting

**If Condition/Action fields don't show dropdowns:**
- Type the field name manually: `destination_number` or `transfer`
- The system should auto-complete or accept the text

**If Context field shows IP address:**
- Clear the field and type: `public`
- This is the context name, not an IP address

**If transfer doesn't work:**
- Check that extension 2001 exists and is registered
- Verify internal context has dialplan for extension 2001
- Check FusionPBX logs: `tail -f /var/log/freeswitch/freeswitch.log`

