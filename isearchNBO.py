import pandas as pd
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog

def browse_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        global directory
        directory = os.path.abspath(directory_path)
        root.destroy()

# Create the main application window
root = tk.Tk()
root.title("first version")
root.configure(bg="black")

# Create a label to display the instructions
instruction_label = tk.Label(root, text="Extracting Summery of Atom Charges", bg="black", fg="white")
instruction_label.pack(padx=100, pady=100)

# Create a label to display the selected directory
selected_directory_label = tk.Label(root, text="Please select a directory of your log files: ", bg="black", fg="white")
selected_directory_label.pack(pady=10)

# Create a button to browse for the directory
browse_button = tk.Button(root, text="Browse", command=browse_directory, padx=10, bg="white", fg="black")
browse_button.pack(pady=5)

# Add a footer label
footer_label = tk.Label(root, text="Written by Samira Baghbanbari", bg="black", fg="gray")
footer_label.pack(side="bottom", pady=5)

root.mainloop()

files_list = []; filenames = []
for filename in sorted(os.listdir(directory))[1:]:
        f = os.path.join(directory, filename)
        if os.path.isfile(f) and f.endswith(".log"):
                files_list.append(f)
                filenames.append(filename)

## Extract some parameters from log file(s)

np_dict = {"Atom": [], "Number": [], "Natural Charge": [], "log filename": []}
for file_path, filename in zip(files_list, filenames):
    with open(file_path, 'r') as file:
        for line_idx, line in enumerate(file):
            if "Summary of Natural Population Analysis:" in line:
                first_line_idx = line_idx
            if "                                Natural Population" in line:
                end_line_idx = line_idx

    with open(file_path, 'r') as file:
        for line_idx, line in enumerate(file):
            if first_line_idx + 6 <= line_idx <= end_line_idx - 4:
                np_dict["Atom"].append(line.strip()[:2])
                np_dict["Number"].append(line.strip()[3:5])
                np_dict["Natural Charge"].append(line.strip()[7:16])
                np_dict["log filename"].append(filename)

df = pd.DataFrame(np_dict)

second_dict = {"log filename": [], "Ru charge": [], "CO charge": [], "PO3 charge": []}
for fname in filenames:
    df1 = df[df["log filename"] == fname]

    if "Ru" in df1["Atom"].unique():
        df_ru = df1[df1["Atom"] == "Ru"]
        ru_charge = float(df_ru["Natural Charge"])
    else:
        ru_charge = pd.NA

    if "C " in df1["Atom"].unique() and len(df1[(df1["Atom"] == "C ") & (df1["Number"] == "1 ")]):
        df_c = df1[(df1["Atom"] == "C ") & (df1["Number"] == "1 ")]
        df_co = df1[(df1["Atom"] == "O ") & (df1["Number"] == "2 ")]
        co_charge = float(df_c["Natural Charge"]) + float(df_co["Natural Charge"])
    else:
        co_charge = pd.NA

    if "P " in df1["Atom"].unique():
        df_po = df1[(df1["Atom"] == "O ") & (df1["Number"].isin(["4 ", "5 ", "6 "]))]
        df_p = df1[(df1["Atom"] == "P ")]
        po3_charge = np.array(df_po["Natural Charge"]).astype(float).sum() + float(df_p["Natural Charge"])
    else:
        po3_charge = pd.NA

    ## missing S, N, Cl, F


    second_dict["log filename"].append(fname)
    second_dict["Ru charge"].append(ru_charge)
    second_dict["CO charge"].append(co_charge)
    second_dict["PO3 charge"].append(po3_charge)

df_sum = pd.DataFrame(second_dict)
df.to_csv(f"{directory}/all_atoms.csv")
df_sum.to_csv(f"{directory}/summery.csv")
