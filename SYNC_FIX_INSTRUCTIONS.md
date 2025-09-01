# 🔄 Data Sync Fix - Complete Instructions

## Status: Phase 2 - Ready for Data Export

✅ **Phase 1 Complete**: Database schema fixed (reflections view created)  
🔄 **Phase 2 Active**: Export localStorage data from both domains

## What Was Fixed

1. **Database Schema**: Created `reflections` view that maps to existing `responses` table
2. **API Compatibility**: Eleanor API can now read/write reflections successfully
3. **Zero Data Loss**: All existing database data (2,451 responses) preserved

## Your Action Required: Export localStorage Data

### Step 1: Export from Desktop (localhost)

1. **Open in browser**: `http://localhost:5173/export-localStorage.html`
2. **Click**: "🔍 Analyze localStorage"
3. **Note**: How many reflections are found
4. **Click**: "📤 Export Reflections" 
5. **Click**: "💾 Download as JSON"
6. **Save as**: `reflections-localhost-{date}.json`

### Step 2: Export from Mobile (IP address)

1. **Open in browser**: `http://192.168.x.x:5173/export-localStorage.html` (your mobile IP)
2. **Click**: "🔍 Analyze localStorage"
3. **Note**: How many reflections are found
4. **Click**: "📤 Export Reflections"
5. **Click**: "💾 Download as JSON"
6. **Save as**: `reflections-mobile-{date}.json`

### Step 3: Compare Results

After both exports, report back with:
- How many reflections were found on localhost?
- How many reflections were found on mobile/IP?
- Were you able to download both JSON files?
- Do the reflection counts match what you expected?

## What Happens Next (After Your Export)

### Phase 3: Migration (Automated)
Once you provide the exported files, I'll:
1. Run the migration script to merge data
2. Import all reflections into the central database
3. Remove duplicates but keep the most recent versions
4. Verify all data was imported correctly

### Phase 4: Frontend Update (Safe)
After successful migration:
1. Update the React app to prioritize database over localStorage
2. Keep localStorage as emergency fallback only
3. Add sync status indicators
4. Test thoroughly before final deployment

### Phase 5: Verification (Complete)
Final verification that:
1. Same reflections appear on both desktop and mobile
2. New reflections save to database immediately
3. No data was lost during migration
4. System remains stable

## Safety Measures in Place

- ✅ **No data deletion** until confirmed working
- ✅ **Multiple backups** created at each step
- ✅ **Rollback procedures** documented and tested
- ✅ **Incremental changes** with verification between each step
- ✅ **Working backup** available from Jan 25 if needed

## Current System Status

- **Eleanor API**: ✅ Running on port 8504
- **Database**: ✅ Connected with 2,451 existing responses
- **Frontend**: ✅ Running on port 5173 (both localhost and IP)
- **Export Tool**: ✅ Available at `/export-localStorage.html`
- **Migration Script**: ✅ Ready and tested

## Emergency Rollback Plan

If anything goes wrong during this process:

```bash
# Stop Eleanor API
docker stop eleanor-api-rtx5090 && docker rm eleanor-api-rtx5090

# Restore from working backup
cp /home/luke/backups_2025_01_25_working/eleanor_quality_api_working.py /home/luke/echosofme-training-tool/eleanor_quality_api.py

# Restart Eleanor API
docker run -d --name eleanor-api-rtx5090 --runtime nvidia -p 8504:8504 -e NVIDIA_VISIBLE_DEVICES=0 -e CUDA_VISIBLE_DEVICES=0 -v /home/luke/echosofme-training-tool:/app -w /app nvcr.io/nvidia/pytorch:25.04-py3 bash -c "pip install -r requirements_rtx5090.txt && python eleanor_quality_api.py"
```

## Questions or Issues?

If you encounter any problems with the export process:
1. Take screenshots of any errors
2. Note which domain you're accessing from
3. Check browser console for error messages (F12 → Console tab)
4. Report back with specific details

---

**Next Step**: Please run the localStorage export on both domains and report your findings!