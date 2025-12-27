import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Halal Lens", page_icon="🔍", layout="wide")

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Please add it to your .streamlit/secrets.toml file.")
    st.stop()

# Using Flash for speed
model = genai.GenerativeModel("gemini-flash-latest")

# --- 2. BETA GATE (THE VELVET ROPE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 1. AUTO-LOGIN: Check if the code is already in the URL
if "code" in st.query_params:
    if st.query_params["code"].upper() == "LENS2025":
        st.session_state.authenticated = True

def check_password():
    if st.session_state.password.upper() == 'LENS2025': 
        st.session_state.authenticated = True
    else:
        st.error("Incorrect access code. Please check your email or DM @khairul.builds")

# 2. THE GATE: Show Login if not authenticated
if not st.session_state.authenticated:
    st.title("Halal Lens 🔍")
    st.caption("The AI Copilot for Halal Grocery Shopping.")
    
    st.warning("🔒 This tool is currently in Private Beta.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_input("Enter Access Code:", key="password", on_change=check_password)
    
    st.markdown("""
        Don't have a code?  
        👉 **[Click here to DM me "BETA" on Instagram to get it instantly!](https://ig.me/m/khairul.builds)**
    """)
    st.stop() # Stops the app here if not logged in

# 3. SUCCESS STATE: If they passed the gate, ensure the URL is saved
# This runs immediately after they log in, forcing the URL to update.
if "code" not in st.query_params:
    st.query_params["code"] = "LENS2025"
    st.rerun() # <--- This magic command forces the browser to refresh with the new URL

# --- 3. SIDEBAR (EDUCATOR MODE) ---
with st.sidebar:
    st.header("Halal Lens 🔍")
    st.caption("v0.2.0 Beta")
    st.markdown("---")
    
    st.subheader("💡 Quick Cheat Sheet")
    st.error("**E120 (Carmine):** 🐞 Crushed beetles (Haram).")
    st.warning("**E441 (Gelatin):** 🍖 Animal bones (Mushbooh).")
    st.warning("**E471:** 🧪 Emulsifier (Mushbooh - check source).")
    
    with st.expander("🇯🇵 Japan/Korea Keywords"):
        st.markdown("""
        * **豚 / 豚肉** (Pork)
        * **酒** (Alcohol/Sake)
        * **みりん** (Mirin)
        * **ゼラチン** (Gelatin)
        * **돼지고기** (Pork)
        * **술** (Alcohol)
        """)
        
    st.markdown("---")
    st.markdown("Found a bug? DM **@khairul.builds**")

# --- 4. MAIN APP INTERFACE ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://em-content.zobj.net/source/microsoft-teams/337/magnifying-glass-tilted-left_1f50d.png", width=80)
with col2:
    st.title("Halal Lens")
    st.write("Decipher foreign snacks instantly. Snap, Upload, Eat (or Don't).")

# 1. The Uploader (Clean, no help text inside)
uploaded_file = st.file_uploader(
    "📸 Take a Photo or Upload from Library", 
    type=["jpg", "jpeg", "png"]
)

# 2. The Tip (Subtle text underneath)
if not uploaded_file:
    st.caption("📱 **Mobile Tip:** If the camera screen is black, check your browser permissions or take the photo normally first, then select 'Photo Library' here.")

# System Prompt for Strict JSON Logic
system_prompt = """
You are a strict Halal Food Auditor. Your job is to analyze ingredient lists from food labels (which may be in English, Chinese, Japanese, Korean, or other languages) and determine their Halal status.

Your analysis must be based on the safest interpretation of Halal dietary laws. 
Follow these rules strictly:

1. **HARAM (Red Flag):** Contains Pork, Lard, Bacon, Ham, Alcohol (Ethanol, Wine, Rum, Brandy), Cochineal (E120), or clear non-halal animal derivatives.
2. **MUSHBOOH (Yellow Flag):** Contains ingredients that *could* be from animal sources but are not specified (e.g., Gelatin, E471, Mono- and diglycerides, Glycerol/E422, Magnesium Stearate, Whey, Rennet, Pepsin) unless explicitly labeled as "Plant-based" or "Vegetarian".
3. **HALAL (Green Flag):** All ingredients are clearly plant-based, aquatic, or synthetic chemicals known to be safe (e.g., Citric Acid, Sugar, Salt, Soy).

**OUTPUT FORMAT:**
Return ONLY a valid JSON object. Do not write any conversational text.
{
  "status": "HALAL" | "MUSHBOOH" | "HARAM",
  "detected_language": "Name of language detected",
  "flagged_ingredients": ["List", "of", "problematic", "ingredients"],
  "reason": "A short, concise explanation of why."
}
"""

if uploaded_file is not None:
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Label", use_column_width=True)

    with col2:
        if st.button("🔍 Scan Ingredients", type="primary", use_container_width=True):
            with st.spinner("Analyzing with Gemini Vision..."):
                try:
                    # Prepare image for API
                    image_parts = [
                        {
                            "mime_type": uploaded_file.type,
                            "data": uploaded_file.getvalue()
                        }
                    ]
                    
                    # Call Gemini
                    response = model.generate_content([system_prompt, image_parts[0]])
                    
                    # Clean response to ensure valid JSON
                    text_response = response.text.strip()
                    if text_response.startswith("```json"):
                        text_response = text_response.replace("```json", "").replace("```", "")
                    
                    # Parse JSON
                    result = json.loads(text_response)
                    
                    # Extract Data
                    status = result.get("status", "MUSHBOOH")
                    language = result.get("detected_language", "Unknown")
                    flags = result.get("flagged_ingredients", [])
                    reason = result.get("reason", "Please verify manually.")

                    # --- TRAFFIC LIGHT UI ---
                    st.caption(f"Detected Language: {language}")

                    if status == "HALAL":
                        st.success("## ✅ VERDICT: HALAL")
                        st.write(f"**Analysis:** {reason}")
                        st.balloons()
                        
                    elif status == "MUSHBOOH":
                        st.warning("## ⚠️ VERDICT: MUSHBOOH (Doubtful)")
                        st.write(f"**Reason:** {reason}")
                        
                        if flags:
                            st.write("---")
                            st.write("**Double Check These:**")
                            for item in flags:
                                st.write(f"- 🟡 {item}")
                        
                        st.info("💡 **Tip:** Look for a 'Halal' logo or 'Vegetarian' label to confirm these.")

                    elif status == "HARAM":
                        st.error("## 🛑 VERDICT: HARAM")
                        st.write(f"**Reason:** {reason}")
                        
                        if flags:
                            st.write("---")
                            st.write("**Non-Halal Ingredients:**")
                            for item in flags:
                                st.write(f"- 🚫 {item}")

                except Exception as e:
                    st.error("Could not analyze image. It might be blurry or the API is busy.")
                    with st.expander("See Error Details"):
                        st.write(e)

# --- FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #888;">
    <small>
    ⚠️ <b>Disclaimer:</b> AI can make mistakes. This tool is for <b>informational purposes only</b>. <br>
    Always verify with official packaging. When in doubt, avoid.
    </small>
</div>
""", unsafe_allow_html=True)
