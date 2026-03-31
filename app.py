import json
import os
import tomllib

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore


def get_firebase_cred():
    if os.path.exists("cloud_credentials.json"):
        return credentials.Certificate("cloud_credentials.json")
    if "firebase" in st.secrets:
        return credentials.Certificate(dict(st.secrets["firebase"]))
    raise RuntimeError("No Firebase credentials found")


def get_passwords():
    if os.path.exists("passwords.toml"):
        with open("passwords.toml", "rb") as f:
            return tomllib.load(f)["passwords"]
    return dict(st.secrets["passwords"])


# --- Firebase Setup ---
if not firebase_admin._apps:
    cred = get_firebase_cred()
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- Config ---
st.set_page_config(page_title="Packing List", layout="centered")

INITIAL_DATA_FILE = "initial_data.json"

# --- User Configuration ---
# To add a user: add an entry here + a matching password in passwords.toml / st.secrets
USERS = {
    "Julianne": {"color": "#eee9e3", "icon": "🐈"},
    "Frida": {"color": "#d4e8ff", "icon": "🌊"},
    "Fred": {"color": "#460096", "icon": "🎮"},
}

# --- Authentication ---
for _key, _default in {"selected_user": None, "authenticated": False}.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default

if not st.session_state.authenticated:
    st.markdown(
        '<style>.stApp { background-color: #f0f0f5; }</style>',
        unsafe_allow_html=True,
    )
    if not st.session_state.selected_user:
        st.title("Welcome! 👋")
        st.write("Choose your profile:")
        for _user, _cfg in USERS.items():
            if st.button(f"{_cfg['icon']} {_user}", key=f"select_{_user}"):
                st.session_state.selected_user = _user
                st.rerun()
    else:
        _user = st.session_state.selected_user
        _cfg = USERS[_user]
        st.title(f"{_cfg['icon']} {_user}")
        _pw = st.text_input("Password", type="password")
        if _pw:
            _passwords = get_passwords()
            if _pw == _passwords.get(_user):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Wrong password")
        if st.button("← Back"):
            st.session_state.selected_user = None
            st.rerun()
    st.stop()

# --- Authenticated: set up user context ---
user_config = USERS[st.session_state.selected_user]
DATA_DOC = db.collection("app_data").document(st.session_state.selected_user)

# --- Styling ---
st.markdown(
    f"""
<style>
.stApp {{ background-color: {user_config["color"]}; }}
.packed-item {{ color: #b0b0b0; text-decoration: line-through; }}
</style>
""",
    unsafe_allow_html=True,
)


# --- Helpers ---
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data():
    DATA_DOC.set(st.session_state.data)


def sync_list():
    if st.session_state.current_name:
        st.session_state.data["packing_lists"][st.session_state.current_name] = \
            st.session_state.packing_list


def sync_module():
    if st.session_state.current_module_name:
        st.session_state.data["activity_modules"][st.session_state.current_module_name] = \
            st.session_state.activities[st.session_state.current_module_name]


def safe_name(name):
    return name.strip().replace("/", "_")

# --- Initialize data (one Firestore read per session) ---
if "data" not in st.session_state:
    _doc = DATA_DOC.get()
    if _doc.exists:
        st.session_state.data = _doc.to_dict()
    else:
        st.session_state.data = load_json(INITIAL_DATA_FILE)
        DATA_DOC.set(st.session_state.data)

data = st.session_state.data
defaults = data["defaults"]

# --- Session state ---
for key, default in {
    "packing_list": {},
    "current_name": None,
    "confirm_delete": False,
    "mode": "generate",
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
st.sidebar.markdown(f"### {user_config['icon']} {st.session_state.selected_user}")
if st.sidebar.button("Save to cloud ☁️"):
    save_data()
    st.sidebar.success("Saved!")
if st.sidebar.button("Log out"):
    st.session_state.clear()
    st.rerun()
st.sidebar.markdown("---")
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
            st.rerun()

    with st.form("add_daily_form", clear_on_submit=True):
        new_daily = st.text_input("Add nightly item")
        if st.form_submit_button("Add nightly item"):
            if new_daily and new_daily not in defaults["daily"]:
                defaults["daily"].append(new_daily)
                st.rerun()

    st.markdown("---")

    st.subheader("Base items (always included)")
    for item in list(defaults["base"]):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_base_{item}"):
            defaults["base"].remove(item)
            st.rerun()

    with st.form("add_base_form", clear_on_submit=True):
        new_base = st.text_input("Add base item")
        if st.form_submit_button("Add base item"):
            if new_base and new_base not in defaults["base"]:
                defaults["base"].append(new_base)
                st.rerun()

    st.markdown("---")

    st.subheader("Base items (only when sleeping over)")
    for item in list(defaults.get("base_sleepover", [])):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_sleepover_{item}"):
            defaults["base_sleepover"].remove(item)
            st.rerun()

    with st.form("add_sleepover_form", clear_on_submit=True):
        new_sleepover = st.text_input("Add sleepover item")
        if st.form_submit_button("Add sleepover item"):
            if new_sleepover and new_sleepover not in defaults.get(
                "base_sleepover", []
            ):
                defaults.setdefault("base_sleepover", []).append(new_sleepover)
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

            st.session_state.current_module_name = new_module_name

            st.rerun()

    st.subheader("Items")
    for item in list(items):
        col1, col2 = st.columns([0.85, 0.15])
        col1.write(item)
        if col2.button("🗑", key=f"del_mod_{item}"):
            items.remove(item)
            sync_module()
            st.rerun()

    with st.form("add_to_module_form", clear_on_submit=True):
        new_item = st.text_input("Add item")
        if st.form_submit_button("Add to module"):
            if new_item and new_item not in items:
                items.append(new_item)
                sync_module()
                st.rerun()

    st.markdown("---")
    if not st.session_state.confirm_module_delete:
        if st.button("Delete module"):
            st.session_state.confirm_module_delete = True
    else:
        st.warning("Are you sure you want to delete this module?")
        col1, col2 = st.columns(2)
        if col1.button("Yes delete module"):
            del data["activity_modules"][st.session_state.current_module_name]
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
                        sync_list()
                        st.rerun()
                with col2:
                    if st.button("🗑", key=f"del_{item}"):
                        del st.session_state.packing_list[item]
                        sync_list()
                        st.rerun()

        st.subheader("Packed")
        for item, packed in list(st.session_state.packing_list.items()):
            if packed:
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    if not st.checkbox(item, value=True, key=f"chk_packed_{item}"):
                        st.session_state.packing_list[item] = False
                        sync_list()
                        st.rerun()
                if col2.button("🗑", key=f"del_p_{item}"):
                    del st.session_state.packing_list[item]
                    sync_list()
                    st.rerun()

        st.markdown("---")
        with st.form("add_custom_item_form", clear_on_submit=True):
            new_item = st.text_input("Add custom item")
            if st.form_submit_button("Add item"):
                if new_item:
                    st.session_state.packing_list[new_item] = False
                    sync_list()
                    st.rerun()

        if st.session_state.mode == "generate":
            st.markdown("---")
            with st.form("save_list_form"):
                name = st.text_input("Save as")
                if st.form_submit_button("Save"):
                    if name:
                        data["packing_lists"][name] = st.session_state.packing_list
                        st.session_state.current_name = name
                        st.session_state.mode = "view"
                        st.success("Saved")
