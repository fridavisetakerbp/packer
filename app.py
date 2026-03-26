import streamlit as st
import os
import json

# --- Config ---
st.set_page_config(page_title="Packing List", layout="centered")

SAVE_LIST_DIR = "packing_lists"
SAVE_MODULE_DIR = "activity_modules"
DEFAULTS_FILE = "defaults.json"

os.makedirs(SAVE_LIST_DIR, exist_ok=True)
os.makedirs(SAVE_MODULE_DIR, exist_ok=True)

# --- Styling ---
st.markdown("""
<style>
.stApp { background-color: #ffe4ec; }
.packed-item { color: #b0b0b0; text-decoration: line-through; }
</style>
""", unsafe_allow_html=True)

# --- Helpers ---
def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def list_saved(path):
    return sorted([f for f in os.listdir(path) if f.endswith(".json")])

def autosave_list():
    if st.session_state.current_file:
        name = st.session_state.current_file.replace(".json", "")
        save_json(os.path.join(SAVE_LIST_DIR, f"{name}.json"), st.session_state.packing_list)

def autosave_module():
    if st.session_state.current_module_file:
        name = st.session_state.current_module_file.replace(".json", "")
        save_json(
            os.path.join(SAVE_MODULE_DIR, f"{name}.json"),
            st.session_state.activities[st.session_state.current_module_name],
        )

# --- Initialize defaults ---
if not os.path.exists(DEFAULTS_FILE):
    save_json(DEFAULTS_FILE, {
        "daily": ["underwear", "socks", "t-shirt"],
        "base": ["toothbrush", "toiletries"]
    })

defaults = load_json(DEFAULTS_FILE)

# --- Session state ---
for key, default in {
    "packing_list": {},
    "current_file": None,
    "current_name": None,
    "confirm_delete": False,
    "mode": "generate",  # generate, view, defaults
    "activities": {},
    "current_module_file": None,
    "current_module_name": None,
    "confirm_module_delete": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Default modules ---
DEFAULT_MODULES = {
    "Running": ["running shoes", "sports socks", "shorts", "t-shirt"],
    "Swimming": ["swimsuit", "towel", "flip flops"],
    "Hiking": ["hiking boots", "backpack", "water bottle", "jacket"],
    "Sleeping": ["pajamas"],
    "Work meetings": ["formal shirt", "formal pants", "belt", "dress shoes"],
    "Coding sessions": ["laptop", "charger", "notebook"],
    "Dinner out": ["nice outfit", "casual shoes"],
}

if not os.listdir(SAVE_MODULE_DIR):
    for k, v in DEFAULT_MODULES.items():
        save_json(os.path.join(SAVE_MODULE_DIR, f"{k}.json"), v)

# Load modules
st.session_state.activities = {}
for f in list_saved(SAVE_MODULE_DIR):
    name = f.replace(".json", "")
    st.session_state.activities[name] = load_json(os.path.join(SAVE_MODULE_DIR, f))

# --- Sidebar ---
st.sidebar.title("My packing lists")

if st.sidebar.button("Generate new packing list"):
    st.session_state.mode = "generate"
    st.session_state.current_file = None
    st.session_state.current_name = None
    st.session_state.packing_list = {}
    st.session_state.current_module_name = None
    st.session_state.current_module_file = None
    st.rerun()

st.sidebar.markdown("### Existing lists")

for file in list_saved(SAVE_LIST_DIR):
    clean_name = file.replace(".json", "")
    if st.sidebar.button(clean_name, key=f"load_list_{file}"):
        st.session_state.packing_list = load_json(os.path.join(SAVE_LIST_DIR, file))
        st.session_state.current_file = file
        st.session_state.current_name = clean_name
        st.session_state.mode = "view"
        st.session_state.current_module_name = None
        st.session_state.current_module_file = None
        st.rerun()

# Delete list
if st.session_state.current_file:
    st.sidebar.markdown("---")
    st.sidebar.write(f"Selected: {st.session_state.current_name}")

    if not st.session_state.confirm_delete:
        if st.sidebar.button("Delete list"):
            st.session_state.confirm_delete = True
    else:
        st.sidebar.warning("Are you sure you want to delete this packing list?")
        col1, col2 = st.sidebar.columns(2)
        if col1.button("Yes"):
            os.remove(os.path.join(SAVE_LIST_DIR, st.session_state.current_file))
            st.session_state.packing_list = {}
            st.session_state.current_file = None
            st.session_state.current_name = None
            st.session_state.confirm_delete = False
            st.session_state.mode = "generate"
            st.rerun()
        if col2.button("Cancel"):
            st.session_state.confirm_delete = False

# --- Modules ---
st.sidebar.markdown("---")
st.sidebar.title("My activities")

new_module_name = st.sidebar.text_input("New module name")
if st.sidebar.button("Create module"):
    if new_module_name and new_module_name not in st.session_state.activities:
        st.session_state.activities[new_module_name] = []
        save_json(os.path.join(SAVE_MODULE_DIR, f"{new_module_name}.json"), [])
        st.session_state.current_module_name = new_module_name
        st.session_state.current_module_file = f"{new_module_name}.json"
        st.session_state.current_file = None
        st.session_state.current_name = None
        st.session_state.mode = "generate"
        st.rerun()

for module in st.session_state.activities:
    if st.sidebar.button(module, key=f"mod_{module}"):
        st.session_state.current_module_name = module
        st.session_state.current_module_file = f"{module}.json"
        st.session_state.current_file = None
        st.session_state.current_name = None
        st.session_state.mode = "generate"
        st.rerun()

# --- Defaults ---
st.sidebar.markdown("---")
st.sidebar.title("Defaults")

if st.sidebar.button("Edit default items"):
    st.session_state.mode = "defaults"
    st.session_state.current_file = None
    st.session_state.current_module_name = None
    st.rerun()

# --- TITLE ---
if st.session_state.current_module_name:
    st.title(st.session_state.current_module_name)
elif st.session_state.mode == "view" and st.session_state.current_name:
    st.title(st.session_state.current_name)
elif st.session_state.mode == "defaults":
    st.title("Default Items")
else:
    st.title("Packing List Generator")

# --- DEFAULTS EDITOR ---
if st.session_state.mode == "defaults":

    st.subheader("Daily items (scaled with days)")
    for item in list(defaults["daily"]):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_daily_{item}"):
            defaults["daily"].remove(item)
            save_json(DEFAULTS_FILE, defaults)
            st.rerun()

    new_daily = st.text_input("Add daily item")
    if st.button("Add daily item"):
        if new_daily and new_daily not in defaults["daily"]:
            defaults["daily"].append(new_daily)
            save_json(DEFAULTS_FILE, defaults)
            st.rerun()

    st.markdown("---")

    st.subheader("Base items (always included)")
    for item in list(defaults["base"]):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_base_{item}"):
            defaults["base"].remove(item)
            save_json(DEFAULTS_FILE, defaults)
            st.rerun()

    new_base = st.text_input("Add base item")
    if st.button("Add base item"):
        if new_base and new_base not in defaults["base"]:
            defaults["base"].append(new_base)
            save_json(DEFAULTS_FILE, defaults)
            st.rerun()

# --- MODULE VIEW ---
elif st.session_state.current_module_name:

    items = st.session_state.activities[st.session_state.current_module_name]

    st.subheader("Items")
    for item in list(items):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_mod_{item}"):
            items.remove(item)
            autosave_module()
            st.rerun()

    new_item = st.text_input("Add item")
    if st.button("Add to module"):
        if new_item and new_item not in items:
            items.append(new_item)
            autosave_module()
            st.rerun()

    st.markdown("---")
    if not st.session_state.confirm_module_delete:
        if st.button("Delete module"):
            st.session_state.confirm_module_delete = True
    else:
        st.warning("Are you sure you want to delete this module?")
        col1, col2 = st.columns(2)
        if col1.button("Yes delete module"):
            os.remove(os.path.join(SAVE_MODULE_DIR, st.session_state.current_module_file))
            del st.session_state.activities[st.session_state.current_module_name]
            st.session_state.current_module_name = None
            st.session_state.current_module_file = None
            st.session_state.confirm_module_delete = False
            st.rerun()
        if col2.button("Cancel"):
            st.session_state.confirm_module_delete = False

# --- PACKING LIST ---
else:

    if st.session_state.mode == "generate":
        selected = st.multiselect("Activities", list(st.session_state.activities.keys()))
        days = st.number_input("Days", 1, 60, 3)

        if st.button("Generate"):
            items = set(defaults["base"])
            for a in selected:
                items.update(st.session_state.activities[a])

            clothing = {item: days for item in defaults["daily"]}

            for k in clothing:
                items.discard(k)

            full = [f"{k} x{v}" for k, v in clothing.items()] + sorted(items)
            st.session_state.packing_list = {i: False for i in full}

    if st.session_state.packing_list:

        st.subheader("To pack")
        for item, packed in list(st.session_state.packing_list.items()):
            if not packed:
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    if st.checkbox(item, key=f"chk_{item}"):
                        st.session_state.packing_list[item] = True
                        autosave_list()
                        st.rerun()
                with col2:
                    if st.button("🗑", key=f"del_{item}"):
                        del st.session_state.packing_list[item]
                        autosave_list()
                        st.rerun()

        st.subheader("Packed")
        for item, packed in list(st.session_state.packing_list.items()):
            if packed:
                col1, col2 = st.columns([0.85, 0.15])
                col1.markdown(f"<div class='packed-item'>☑ {item}</div>", unsafe_allow_html=True)
                if col2.button("🗑", key=f"del_p_{item}"):
                    del st.session_state.packing_list[item]
                    autosave_list()
                    st.rerun()

        st.markdown("---")
        new_item = st.text_input("Add custom item")
        if st.button("Add item"):
            if new_item:
                st.session_state.packing_list[new_item] = False
                autosave_list()
                st.rerun()

        if st.session_state.mode == "generate":
            st.markdown("---")
            name = st.text_input("Save as")
            if st.button("Save"):
                if name:
                    save_json(os.path.join(SAVE_LIST_DIR, f"{name}.json"), st.session_state.packing_list)
                    st.session_state.current_file = f"{name}.json"
                    st.session_state.current_name = name
                    st.session_state.mode = "view"
                    st.success("Saved")