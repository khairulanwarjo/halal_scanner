import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION & SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Please add it to your .streamlit/secrets.toml file.")

model = genai.GenerativeModel("gemini-flash-latest")

# Page Config
st.set_page_config(page_title="Global Halal Scanner", page_icon="🌏", layout="wide")

# --- 2. SIDEBAR (CHEAT SHEET) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5141/5141534.png", width=80)
    st.title("Halal Guide 📖")
    st.write("Quick references for your travels.")

    # Section 1: E-Codes
    with st.expander("⚠️ Common E-Codes to Watch"):
        st.markdown("""
        **Haram (Usually):**
        * **E120** (Cochineal/Carmine) - Insect
        * **E441** (Gelatin) - Animal Bone
        * **E542** (Bone Phosphate) - Animal Bone
        
        **Mushbooh (Doubtful):**
        * **E471** (Emulsifier) - Plant or Animal?
        * **E422** (Glycerol)
        * **E470-E483** (Fatty Acids)
        """)
    
    # Section 2: Common Terms
    with st.expander("🇯🇵 Japan/Korea Keywords"):
        st.markdown("""
        **Look out for these symbols:**
        * **豚 / 豚肉** (Pork)
        * **酒** (Alcohol/Sake)
        * **みりん** (Mirin - Rice Wine)
        * **ゼラチン** (Gelatin)
        * **돼지고기** (Pork - Korean)
        * **술** (Alcohol - Korean)
        """)

    st.info("💡 **Tip:** E471 is very common. It is only Halal if marked 'Plant-based' or 'Soy origin'.")

    # --- NEW ADDITION: SIDEBAR DISCLAIMER ---
    st.divider()
    st.caption("⚠️ **Disclaimer:** This tool uses Artificial Intelligence. It may make mistakes. Always verify with official Halal certification bodies.")

# --- 3. MAIN APP INTERFACE ---
st.title("Global Halal Scanner 🌏")
st.markdown("""
**Upload an ingredients label in ANY language.** We will detect the language, translate it, and identify non-halal ingredients for you.
""")

# File Uploader
uploaded_file = st.file_uploader("📸 Snap or Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Create two columns: Image on Left, Results on Right
    col1, col2 = st.columns([1, 2])
    
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Label", use_column_width=True)

    with col2:
        # Analyze Button
        if st.button("🔍 Check Ingredients", use_container_width=True):
            with st.spinner("Translating & Scanning..."):
                try:
                    # --- PROMPT ENGINEERING ---
                    prompt = """
                    You are a strict Halal food expert and nutritionist. 
                    Analyze the text in this image. The text might be in ANY language.

                    Your goal is to educate the user on WHICH ingredients are problematic and WHY.

                    Please output your response following this EXACT structure:

                    Line 1: VERDICT_RESULT (Only output one word: HALAL, HARAM, or MUSHBOOH)
                    Line 2: Detected Language: [Language Name]
                    Line 3: ---
                    
                    Then, provide the details in Markdown format:

                    ### 🔴 Haram Ingredients (Forbidden)
                    (Create a Markdown table with columns: 'Ingredient (Original)', 'English Translation', 'Reason for Prohibition'. If none found, write "None detected".)

                    ### 🟡 Mushbooh Ingredients (Doubtful/Syubhah)
                    (Create a Markdown table with columns: 'Ingredient (Original)', 'English Translation', 'Reason for Doubt'. If none found, write "None detected".)

                    ### 📝 Nutritionist's Verdict
                    (A short summary of the overall status and any helpful advice for a Muslim traveler.)
                    """
                    
                    response = model.generate_content([prompt, image])
                    full_text = response.text
                    
                    # --- PARSING LOGIC ---
                    lines = full_text.split('\n')
                    
                    if lines:
                        verdict = lines[0].replace("VERDICT_RESULT", "").strip().upper()
                    else:
                        verdict = "ERROR"
                    
                    # Find where explanation starts
                    explanation_start_index = 0
                    for i, line in enumerate(lines):
                        if "---" in line:
                            explanation_start_index = i + 1
                            break
                    
                    explanation = "\n".join(lines[explanation_start_index:])
                    
                    # Extract Language
                    detected_lang = "Language: Unknown"
                    for line in lines[:5]: 
                        if "Detected Language:" in line:
                            detected_lang = line.strip()

                    # --- DISPLAY RESULTS ---
                    if "HARAM" in verdict:
                        st.error(f"🚨 **VERDICT: HARAM**")
                        st.caption(detected_lang)
                        st.markdown(explanation)
                    
                    elif "MUSHBOOH" in verdict:
                        st.warning(f"⚠️ **VERDICT: MUSHBOOH (Doubtful)**")
                        st.caption(detected_lang)
                        st.markdown(explanation)
                    
                    elif "HALAL" in verdict:
                        st.success(f"✅ **VERDICT: HALAL**")
                        st.caption(detected_lang)
                        st.markdown(explanation)
                        
                    else:
                        st.info("Verdict: Analysis Complete")
                        st.write(full_text)

                except Exception as e:
                    st.error(f"An error occurred: {e}")

# --- NEW ADDITION: FOOTER DISCLAIMER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #888;">
    <small>
    ⚠️ <b>Disclaimer:</b> This application uses Google Gemini AI to analyze ingredients. <br>
    AI can hallucinate or misread text. This tool is for <b>informational purposes only</b> and does not constitute a fatwa or official Halal certification. <br>
    When in doubt, it is safer to avoid.
    </small>
</div>
""", unsafe_allow_html=True)
