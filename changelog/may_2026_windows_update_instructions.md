# Upgrading Lean Hogs Analysis — Windows

**What's changing:** The app no longer connects to the internet to fetch prices. Instead it reads directly from an Excel file you keep updated yourself. You'll copy new program files, add the data file, and run two commands to update the environment.

**Time required:** ~10 minutes.

---

## Step 1 — Copy the new program files

Copy the following files from the update package into your existing project folder (the same folder where `Lean_Hogs_v5.ipynb` already lives). If Windows asks whether to replace existing files, click **Replace**.

Files to copy:
- `Lean_Hogs_v5.ipynb`
- `uicontrollerv2.py`
- `dataManager.py`
- `controller.py`
- `butterfly.py`
- `lhdata.py`

---

## Step 2 — Add the settlement data file

Copy `hog_settlements.xlsx` into the same project folder. This file replaces the old `.pickle` files — you can delete `data.pickle` and `data.hist.pickle` if you see them there, they are no longer used.

**Going forward**, when you receive updated settlement data, replace this file with the new version. The filename must stay exactly `hog_settlements.xlsx`.

---

## Step 3 — Open Anaconda Prompt

Click the Windows **Start** menu and search for **Anaconda Prompt**. Open it. You'll see a black window with a command prompt — this is normal.

---

## Step 4 — Navigate to the project folder

Type the following, replacing the path with wherever your project folder actually is, then press Enter:

```
cd "C:\Users\YourName\Documents\LeanHogs"
```

If you're not sure of the path, open the project folder in File Explorer, click on the address bar at the top, and copy the path shown there.

---

## Step 5 — Update the environment

Run these two commands one at a time, pressing Enter after each and waiting for each to finish:

```
conda activate hogs
conda env update -f conda\environment.yml --prune
```

The prompt should change to show `(hogs)` after the first command. The second may take a minute — wait for `done` to appear before continuing.

---

## Step 6 — Launch Jupyter

```
jupyter notebook
```

A browser tab will open. Click on `Lean_Hogs_v5.ipynb` to open it.

---

## Step 7 — Run the notebook

Click inside the single code cell and press **Shift + Enter** (hold Shift, then press Enter). The interface should load within a few seconds.

You should see the **DATA FILE** field at the top already showing `hog_settlements.xlsx`. If your data file is in a different location, use the **Browse...** button to locate it.

---

## Troubleshooting

| Problem | What to try |
|---|---|
| `ModuleNotFoundError: No module named 'xlrd'` | Step 5 didn't complete — run the two commands again |
| `FileNotFoundError: Data file 'hog_settlements.xlsx' not found` | The data file isn't in the project folder, or has a different name — check spelling and location |
| The status bar shows a red error message | The error text describes the problem — screenshot it and send to support |
| Charts don't appear in a separate window | Make sure the first line of the notebook cell reads `%matplotlib qt` (not `%matplotlib inline`) |
