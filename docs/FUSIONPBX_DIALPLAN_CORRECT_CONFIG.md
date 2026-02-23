# FusionPBX Dialplan - Correct Configuration

## Issue with Current Configuration

Looking at your screenshot:
- ❌ **Condition 1:** `context = public` - **WRONG!** Remove this.
- ✅ **Condition 2:** `destination_number = ^2001$` - **CORRECT!**
- ✅ **Action 1:** `transfer=2001 XML internal` - **CORRECT!** (but check format)
- ✅ **Context:** `public` - **CORRECT!**
- ✅ **Order:** `200` - **CORRECT!**
- ✅ **Enabled:** `True` - **CORRECT!**

## Why Condition 1 is Wrong

The `context = public` condition is **redundant** because:
1. The dialplan entry is already in the `public` context (set in the Context field)
2. Only calls that match the context will reach this dialplan entry
3. Checking context again is unnecessary and can cause issues

## Correct Configuration

### Remove Condition 1

1. **Find Condition 1** (the one with `context = public`)
2. **Remove it** - click the delete/remove button or clear the fields
3. **Keep only Condition 2** (`destination_number = ^2001$`)

### Final Configuration Should Be:

**Conditions:**
- **Condition 1:** `destination_number` = `^2001$` (ONLY this one)

**Actions:**
- **Action 1:** 
  - Action name: `transfer`
  - Value: `2001 XML internal`
  - (If your UI has separate fields, use them. If it's one field, `transfer=2001 XML internal` is fine)

**Other Fields:**
- **Name:** `Twilio-to-Extension-2001`
- **Context:** `public`
- **Order:** `200`
- **Enabled:** `True`
- **Description:** `Route Twilio calls to extension 2001` (optional)

## Action Format Check

If your Action field shows `transfer=2001 XML internal` as one value, that's fine.

If you have separate fields for Action name and Value:
- **Action 1 Name:** `transfer`
- **Action 1 Value:** `2001 XML internal`

## Step-by-Step Fix

1. **Remove Condition 1** (`context = public`)
   - Delete or clear the `context` and `public` fields in Condition 1
   - Or remove Condition 1 entirely if possible

2. **Keep Condition 2** (`destination_number = ^2001$`)
   - This is correct, don't change it

3. **Verify Action 1**
   - Should be: `transfer=2001 XML internal`
   - Or if separate fields: Action = `transfer`, Value = `2001 XML internal`

4. **Click "SAVE"**

5. **Reload XML:**
   ```bash
   fs_cli -x "reloadxml"
   ```

## Why This Matters

Having `context = public` as a condition can cause the dialplan to not match correctly because:
- The dialplan is already in the `public` context
- FreeSWITCH might interpret this condition differently than expected
- It's redundant and can cause routing issues

**Solution:** Remove Condition 1, keep only the `destination_number` condition.

