import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# -----------------------------------------------
# PAGE CONFIG — must be the first Streamlit call
# -----------------------------------------------
st.set_page_config(
    page_title="Food Calorie Tracker",
    page_icon="🍽️",
    layout="centered"
)

# -----------------------------------------------
# CUSTOM STYLING
# -----------------------------------------------
st.markdown("""
    <style>
    /* Import Inter font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Apply Inter to everything */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Style the main title */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
    }

    /* Style the file upload box */
    [data-testid="stFileUploader"] {
        border: 2px dashed #FF6B6B;
        border-radius: 16px;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# GEMINI SETUP
# -----------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# -----------------------------------------------
# HELPER FUNCTION — Ask Gemini to analyze food
# -----------------------------------------------


def analyze_food(image: Image.Image) -> dict:
    """
    Sends the image to Gemini and asks it to return
    nutritional info as JSON.
    """
    prompt = """
    You are a nutrition expert. Analyze this food image and return ONLY a JSON object.
    No extra text, no markdown, just the raw JSON.

    Return this exact structure:
    {
        "food_name": "name of the food",
        "description": "one sentence describing the dish",
        "calories": number,
        "protein_g": number,
        "carbs_g": number,
        "fat_g": number,
        "fiber_g": number,
        "serving_size": "estimated serving size (e.g. 1 plate, 200g)",
        "health_score": number from 1 to 10,
        "insight": "one helpful nutrition tip about this food",
        "good_for": ["list", "of", "health", "benefits"],
        "watch_out": "one thing to be mindful of when eating this"
    }

    If you cannot identify food in the image, return:
    {
        "food_name": "Unknown",
        "description": "Could not identify food in this image.",
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fat_g": 0,
        "fiber_g": 0,
        "serving_size": "N/A",
        "health_score": 0,
        "insight": "Please try a clearer photo of food.",
        "good_for": [],
        "watch_out": "N/A"
    }
    """
    response = model.generate_content([prompt, image])
    raw = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# -----------------------------------------------
# UI — Title & Description
# -----------------------------------------------
st.title("🍽️ Food Calorie Tracker")
st.markdown(
    "Upload a photo of your food and get instant nutritional information powered by AI.")
st.divider()

# -----------------------------------------------
# UI — File Upload
# -----------------------------------------------
uploaded_file = st.file_uploader(
    "Upload a food photo",
    type=["jpg", "jpeg", "png", "webp"],
    help="Take a photo of your meal and upload it here"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your uploaded food photo", use_column_width=True)
    st.divider()

    if st.button("🔍 Analyze Food", type="primary", use_container_width=True):
        with st.spinner("Identifying your food and calculating nutrition..."):
            try:
                data = analyze_food(image)

                # -----------------------------------------------
                # RESULTS — Food name & description
                # -----------------------------------------------
                st.subheader(f"🍴 {data['food_name']}")
                st.caption(data["description"])
                st.caption(f"Estimated serving: {data['serving_size']}")
                st.divider()

                # -----------------------------------------------
                # RESULTS — Macro cards (custom HTML)
                # -----------------------------------------------
                st.markdown(f"""
    <div style="display:flex; gap:1rem; margin:1rem 0;">
        <div style="flex:1; background:#fff5f5; border-radius:16px; padding:1.25rem;">
            <p style="font-size:0.8rem; color:#888; margin:0; text-align:center;">🔥 Calories</p>
           <p style="font-size:1.75rem; font-weight:700; margin:0.25rem 0; text-align:center; display:block; width:100%; font-family:'Inter',sans-serif;">{data['calories']}</p>
            <p style="font-size:0.75rem; color:#aaa; margin:0; text-align:center;">kcal</p>
        </div>
        <div style="flex:1; background:#f0f7ff; border-radius:16px; padding:1.25rem;">
            <p style="font-size:0.8rem; color:#888; margin:0; text-align:center;">💪 Protein</p>
            <p style="font-size:1.75rem; font-weight:700; margin:0.25rem 0; text-align:center; display:block; width:100%; font-family:'Inter',sans-serif;">{data['protein_g']}</p>
            <p style="font-size:0.75rem; color:#aaa; margin:0; text-align:center;">grams</p>
        </div>
        <div style="flex:1; background:#fff8f0; border-radius:16px; padding:1.25rem;">
            <p style="font-size:0.8rem; color:#888; margin:0; text-align:center;">🍞 Carbs</p>
            <p style="font-size:1.75rem; font-weight:700; margin:0.25rem 0; text-align:center; display:block; width:100%; font-family:'Inter',sans-serif;">{data['carbs_g']}</p>
            <p style="font-size:0.75rem; color:#aaa; margin:0; text-align:center;">grams</p>
        </div>
        <div style="flex:1; background:#f2fff5; border-radius:16px; padding:1.25rem;">
            <p style="font-size:0.8rem; color:#888; margin:0; text-align:center;">🥑 Fat</p>
            <p style="font-size:1.75rem; font-weight:700; margin:0.25rem 0; text-align:center; display:block; width:100%; font-family:'Inter',sans-serif;">{data['fat_g']}</p>
            <p style="font-size:0.75rem; color:#aaa; margin:0; text-align:center;">grams</p>
        </div>
    </div>
""", unsafe_allow_html=True)
                st.divider()

                # -----------------------------------------------
                # RESULTS — Macro breakdown bars
                # -----------------------------------------------
                st.subheader("📊 Macro Breakdown")
                total = data["protein_g"] + data["carbs_g"] + data["fat_g"]
                if total > 0:
                    prot_pct = round((data["protein_g"] / total) * 100)
                    carb_pct = round((data["carbs_g"] / total) * 100)
                    fat_pct = round((data["fat_g"] / total) * 100)

                    st.markdown(
                        f"**Protein** — {data['protein_g']}g ({prot_pct}%)")
                    st.progress(prot_pct / 100)
                    st.markdown(
                        f"**Carbs** — {data['carbs_g']}g ({carb_pct}%)")
                    st.progress(carb_pct / 100)
                    st.markdown(f"**Fat** — {data['fat_g']}g ({fat_pct}%)")
                    st.progress(fat_pct / 100)
                    st.markdown(f"**Fiber** — {data['fiber_g']}g")
                st.divider()

                # -----------------------------------------------
                # RESULTS — Health score
                # -----------------------------------------------
                st.subheader("❤️ Health Score")
                score = data["health_score"]
                score_color = "🟢" if score >= 7 else "🟡" if score >= 4 else "🔴"
                st.markdown(f"### {score_color} {score} / 10")
                st.progress(score / 10)
                st.divider()

                # -----------------------------------------------
                # RESULTS — Good for & watch out
                # -----------------------------------------------
                col_good, col_watch = st.columns(2)
                with col_good:
                    st.subheader("✅ Good for")
                    if data["good_for"]:
                        for benefit in data["good_for"]:
                            st.markdown(f"- {benefit}")
                    else:
                        st.markdown("No specific benefits identified.")
                with col_watch:
                    st.subheader("⚠️ Watch out")
                    st.markdown(data["watch_out"])
                st.divider()

                # -----------------------------------------------
                # RESULTS — Nutrition insight
                # -----------------------------------------------
                st.info(f"💡 **Nutrition Insight:** {data['insight']}")

            except json.JSONDecodeError:
                st.error(
                    "The AI returned an unexpected response. Please try again with a clearer food photo.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

else:
    st.markdown("""
    ### How it works
    1. Take a photo of your meal
    2. Upload it above
    3. AI identifies the food and calculates nutrition
    4. Get instant calorie & macro breakdown
    """)
