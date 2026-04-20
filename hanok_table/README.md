# Hanok Table (vendored in 7-gcconvonet)

This directory must contain the **Hanok Table** Python package (same layout as in your local `kfood/hanok_table` tree).

**One-time populate (from existing `kfood/` on your machine, no GitHub clone required):**

```bash
# From repository root
rsync -a --delete kfood/hanok_table/ ./hanok_table/
# or: cp -R kfood/hanok_table/. ./hanok_table/
```

Then commit `hanok_table/` so Cloud Build receives it. Build with `docker/hanok-table.Dockerfile` or `cloudbuild-hanok-table.yaml`.
