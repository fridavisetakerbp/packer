import json
import os
import shutil

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def get_firebase_cred():
    # Case 1: Running on Streamlit Cloud
    if "firebase" in st.secrets:
        return credentials.Certificate(dict(st.secrets["firebase"]))
    
    # Case 2: Local development
    elif os.path.exists("cloud_credentials.json"):
        return credentials.Certificate("cloud_credentials.json")
    
    else:
        raise RuntimeError("No Firebase credentials found")

# --- Firebase Setup ---
if not firebase_admin._apps:  # check if Firebase app is already initialized
    cred = get_firebase_cred()
    firebase_admin.initialize_app(cred)
    
db = firestore.client()

# --- Config ---
st.set_page_config(page_title="Packing List", layout="centered")

DATA_FILE = "data.json"
INITIAL_DATA_FILE = "initial_data.json"

# --- Styling ---
st.markdown(
    """
<style>
.stApp { background-color: #ffe4ec; }
.packed-item { color: #b0b0b0; text-decoration: line-through; }
</style>
""",
    unsafe_allow_html=True,
)


# --- Helpers ---
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def autosave_list():
    if st.session_state.current_name:
        data["packing_lists"][st.session_state.current_name] = st.session_state.packing_list
        save_data()


def autosave_module():
    if st.session_state.current_module_name:
        data["activity_modules"][st.session_state.current_module_name] = \
            st.session_state.activities[st.session_state.current_module_name]
        save_data()


def safe_name(name):
    return name.strip().replace("/", "_")

# --- Initialize data ---
if not os.path.exists(DATA_FILE):
    shutil.copy2(INITIAL_DATA_FILE, DATA_FILE)

data = load_json(DATA_FILE)
defaults = data["defaults"]

# --- Session state ---
for key, default in {
    "packing_list": {},
    "current_name": None,
    "confirm_delete": False,
    "mode": "generate",  # generate, view, defaults
    "activities": {},
    "current_module_name": None,
    "confirm_module_delete": False,
    "new_module_items": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Load modules
st.session_state.activities = data["activity_modules"]

# --- Sidebar ---
st.sidebar.title("My packing lists")

if st.sidebar.button("Generate new packing list"):
    st.session_state.mode = "generate"
    st.session_state.current_name = None
    st.session_state.packing_list = {}
    st.session_state.current_module_name = None
    st.session_state.new_module_items = []
    st.rerun()

st.sidebar.markdown("### Existing lists")

for name in sorted(data["packing_lists"]):
    if st.sidebar.button(name, key=f"load_list_{name}"):
        st.session_state.packing_list = data["packing_lists"][name]
        st.session_state.current_name = name
        st.session_state.mode = "view"
        st.session_state.current_module_name = None
        st.session_state.new_module_items = []
        st.rerun()

# Delete list
if st.session_state.current_name:
    st.sidebar.markdown("---")
    st.sidebar.write(f"Selected: {st.session_state.current_name}")

    new_name = st.sidebar.text_input(
        "Rename list", value=st.session_state.current_name, key="rename_list_input"
    )

    if st.sidebar.button("Rename list"):
        new_name = safe_name(new_name)

        if new_name in data["packing_lists"]:
            st.sidebar.error("Name already exists")
        elif new_name != st.session_state.current_name:
            data["packing_lists"][new_name] = data["packing_lists"].pop(
                st.session_state.current_name
            )
            save_data()
            st.session_state.current_name = new_name
            st.rerun()

    if not st.session_state.confirm_delete:
        if st.sidebar.button("Delete list"):
            st.session_state.confirm_delete = True
    else:
        st.sidebar.warning("Are you sure you want to delete this packing list?")
        col1, col2 = st.sidebar.columns(2)
        if col1.button("Yes"):
            del data["packing_lists"][st.session_state.current_name]
            save_data()
            st.session_state.packing_list = {}
            st.session_state.current_name = None
            st.session_state.confirm_delete = False
            st.session_state.mode = "generate"
            st.rerun()
        if col2.button("Cancel"):
            st.session_state.confirm_delete = False

# --- Modules ---
st.sidebar.markdown("---")
st.sidebar.title("My activities")

if st.sidebar.button("Create new module"):
    st.session_state.mode = "create_module"
    st.session_state.current_module_name = None
    st.session_state.current_name = None
    st.session_state.new_module_items = []
    st.rerun()

for module in st.session_state.activities:
    if st.sidebar.button(module, key=f"mod_{module}"):
        st.session_state.current_module_name = module
        st.session_state.current_name = None
        st.session_state.mode = "generate"
        st.session_state.new_module_items = []
        st.rerun()

# --- Defaults ---
st.sidebar.markdown("---")
st.sidebar.title("Defaults")

if st.sidebar.button("Edit default items"):
    st.session_state.mode = "defaults"
    st.session_state.current_name = None
    st.session_state.current_module_name = None
    st.session_state.new_module_items = []
    st.rerun()

# --- TITLE ---
if st.session_state.mode == "create_module":
    st.title("Module Generator")
elif st.session_state.current_module_name:
    st.title(st.session_state.current_module_name)
elif st.session_state.mode == "view" and st.session_state.current_name:
    st.title(st.session_state.current_name)
elif st.session_state.mode == "defaults":
    st.title("Default Items")
else:
    st.title("Packing List Generator")

# --- MODULE GENERATOR ---
if st.session_state.mode == "create_module":
    module_name = st.text_input("Module name")

    st.subheader("Items")
    for i, item in enumerate(list(st.session_state.new_module_items)):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_new_mod_{i}"):
            st.session_state.new_module_items.remove(item)
            st.rerun()

    with st.form("add_new_module_item_form", clear_on_submit=True):
        new_item = st.text_input("Add item")
        if st.form_submit_button("Add"):
            if new_item and new_item not in st.session_state.new_module_items:
                st.session_state.new_module_items.append(new_item)
                st.rerun()

    st.markdown("---")
    if st.button("Create module"):
        if not module_name:
            st.error("Please enter a module name.")
        elif module_name in st.session_state.activities:
            st.error(f"A module named '{module_name}' already exists.")
        else:
            st.session_state.activities[module_name] = list(
                st.session_state.new_module_items
            )
            data["activity_modules"][module_name] = list(
                st.session_state.new_module_items
            )
            save_data()
            st.session_state.current_module_name = module_name
            st.session_state.new_module_items = []
            st.session_state.mode = "generate"
            st.rerun()

# --- DEFAULTS EDITOR ---
elif st.session_state.mode == "defaults":
    st.subheader("Nightly items (scaled with nights)")
    for item in list(defaults["daily"]):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_daily_{item}"):
            defaults["daily"].remove(item)
            save_data()
            st.rerun()

    with st.form("add_daily_form", clear_on_submit=True):
        new_daily = st.text_input("Add nightly item")
        if st.form_submit_button("Add nightly item"):
            if new_daily and new_daily not in defaults["daily"]:
                defaults["daily"].append(new_daily)
                save_data()
                st.rerun()

    st.markdown("---")

    st.subheader("Base items (always included)")
    for item in list(defaults["base"]):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_base_{item}"):
            defaults["base"].remove(item)
            save_data()
            st.rerun()

    with st.form("add_base_form", clear_on_submit=True):
        new_base = st.text_input("Add base item")
        if st.form_submit_button("Add base item"):
            if new_base and new_base not in defaults["base"]:
                defaults["base"].append(new_base)
                save_data()
                st.rerun()

    st.markdown("---")

    st.subheader("Base items (only when sleeping over)")
    for item in list(defaults.get("base_sleepover", [])):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_sleepover_{item}"):
            defaults["base_sleepover"].remove(item)
            save_data()
            st.rerun()

    with st.form("add_sleepover_form", clear_on_submit=True):
        new_sleepover = st.text_input("Add sleepover item")
        if st.form_submit_button("Add sleepover item"):
            if new_sleepover and new_sleepover not in defaults.get(
                "base_sleepover", []
            ):
                defaults.setdefault("base_sleepover", []).append(new_sleepover)
                save_data()
                st.rerun()

# --- MODULE VIEW ---
elif st.session_state.current_module_name:
    items = st.session_state.activities[st.session_state.current_module_name]
    # --- Rename module ---
    current_name = st.session_state.current_module_name

    new_module_name = st.text_input(
        "Rename module", value=current_name, key="rename_module_input"
    )

    if st.button("Rename module"):
        new_module_name = safe_name(new_module_name)

        if new_module_name in st.session_state.activities:
            st.error("Module already exists")
        elif new_module_name != current_name:
            st.session_state.activities[new_module_name] = \
                st.session_state.activities.pop(current_name)
            data["activity_modules"][new_module_name] = \
                data["activity_modules"].pop(current_name)
            save_data()

            st.session_state.current_module_name = new_module_name

            st.rerun()

    st.subheader("Items")
    for item in list(items):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_mod_{item}"):
            items.remove(item)
            autosave_module()
            st.rerun()

    with st.form("add_to_module_form", clear_on_submit=True):
        new_item = st.text_input("Add item")
        if st.form_submit_button("Add to module"):
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
            del st.session_state.activities[st.session_state.current_module_name]
            del data["activity_modules"][st.session_state.current_module_name]
            save_data()
            st.session_state.current_module_name = None
            st.session_state.confirm_module_delete = False
            st.rerun()
        if col2.button("Cancel"):
            st.session_state.confirm_module_delete = False

# --- PACKING LIST ---
else:
    if st.session_state.mode == "generate":
        selected = st.multiselect(
            "Activities", list(st.session_state.activities.keys())
        )
        days = st.number_input("Nights", 0, 60, 3)

        if st.button("Generate"):
            items = set()
            items.update(defaults["base"])
            for a in selected:
                items.update(st.session_state.activities[a])

            if days > 0:
                items.update(defaults.get("base_sleepover", []))
                clothing = {item: days for item in defaults["daily"]}
                for k in clothing:
                    items.discard(k)
                full = [f"{k} x{v}" for k, v in clothing.items()] + sorted(items)
            else:
                full = sorted(items)
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
                with col1:
                    if not st.checkbox(item, value=True, key=f"chk_packed_{item}"):
                        st.session_state.packing_list[item] = False
                        autosave_list()
                        st.rerun()
                if col2.button("🗑", key=f"del_p_{item}"):
                    del st.session_state.packing_list[item]
                    autosave_list()
                    st.rerun()

        st.markdown("---")
        with st.form("add_custom_item_form", clear_on_submit=True):
            new_item = st.text_input("Add custom item")
            if st.form_submit_button("Add item"):
                if new_item:
                    st.session_state.packing_list[new_item] = False
                    autosave_list()
                    st.rerun()

        if st.session_state.mode == "generate":
            st.markdown("---")
            with st.form("save_list_form"):
                name = st.text_input("Save as")
                if st.form_submit_button("Save"):
                    if name:
                        data["packing_lists"][name] = st.session_state.packing_list
                        save_data()
                        st.session_state.current_name = name
                        st.session_state.mode = "view"
                        st.success("Saved")
