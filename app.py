# app.py ── KrishiSahay Smart Farming Platform
# restructured for modularity, UI/UX and new features

import streamlit as st
from dotenv import load_dotenv
import PIL.Image
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go

load_dotenv()

# core business logic modules
from crop_model import recommend_crop
from disease_model import predict_disease
from fertilizer_model import recommend_fertilizer
from weather import fetch_weather, advice_from_weather
from market_price import get_current_price, predict_price_trend, available_crops, get_price_chart
from utils import t, load_css
from chat_service import bubble_html, generate_response, record_chat_message, timestamp, transcribe_audio

# --- UI components --------------------------------------------------------------

def show_dashboard(lang):
    st.markdown('<div class="section-kicker">Field operations / Telangana</div>', unsafe_allow_html=True)
    st.header("Good evening, farmer", icon=":material/dashboard:")
    st.caption("A live snapshot of your growing conditions, crop health, and farm priorities.")

    weather = fetch_weather()
    temperature = weather["temp"] if weather else 28.4
    humidity = weather["humidity"] if weather else 62
    moisture = 58
    water_level = 74

    kpi_one, kpi_two, kpi_three, kpi_four = st.columns(4)
    with kpi_one:
        st.metric("Soil moisture", f"{moisture}%", "+4.2%", icon=":material/water_drop:")
    with kpi_two:
        st.metric("Temperature", f"{temperature:.1f} °C", "Within range", icon=":material/device_thermostat:")
    with kpi_three:
        st.metric("Humidity", f"{humidity}%", "Stable", icon=":material/humidity_high:")
    with kpi_four:
        st.metric("Water level", f"{water_level}%", "Ready for 3 days", icon=":material/opacity:")

    dates = [datetime.now() - timedelta(days=day) for day in range(6, -1, -1)]
    moisture_values = [49, 53, 51, 56, 54, 57, moisture]
    temperature_values = [27.1, 28.4, 29.0, 28.2, 27.8, 28.9, temperature]
    chart_one, chart_two = st.columns(2)
    with chart_one:
        st.subheader("Soil moisture trend", icon=":material/water_drop:")
        moisture_chart = go.Figure(go.Scatter(
            x=dates, y=moisture_values, mode="lines+markers",
            line={"color": "#2e7d32", "width": 3}, marker={"size": 7, "color": "#b47c3c"},
        ))
        moisture_chart.update_layout(height=260, margin={"l": 10, "r": 10, "t": 15, "b": 10},
                                     paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f7faf4",
                                     yaxis={"title": "%", "range": [35, 75]}, xaxis={"showgrid": False})
        st.plotly_chart(moisture_chart, width="stretch", key="moisture_trend")
    with chart_two:
        st.subheader("Temperature trend", icon=":material/device_thermostat:")
        temperature_chart = go.Figure(go.Scatter(
            x=dates, y=temperature_values, mode="lines+markers",
            line={"color": "#c47f35", "width": 3}, marker={"size": 7, "color": "#1b5e20"},
        ))
        temperature_chart.update_layout(height=260, margin={"l": 10, "r": 10, "t": 15, "b": 10},
                                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fffaf3",
                                        yaxis={"title": "°C"}, xaxis={"showgrid": False})
        st.plotly_chart(temperature_chart, width="stretch", key="temperature_trend")

    st.subheader("Today’s priorities", icon=":material/task_alt:")
    priority_one, priority_two, priority_three = st.columns(3)
    with priority_one:
        st.success("**Irrigation**\n\nMoisture is healthy. Recheck the root zone tomorrow morning.", icon=":material/check_circle:")
    with priority_two:
        st.warning("**Crop scouting**\n\nInspect cotton squares for early pink bollworm signs.", icon=":material/search:")
    with priority_three:
        st.info("**Market check**\n\nReview the latest price before committing your harvest.", icon=":material/analytics:")

    st.subheader("Recent farm activity", icon=":material/history:")
    history = pd.DataFrame([
        {"Date": "16 Sep 2026", "Activity": "Soil moisture check", "Crop": "Cotton", "Status": "Healthy"},
        {"Date": "15 Sep 2026", "Activity": "Crop recommendation", "Crop": "Paddy", "Status": "Completed"},
        {"Date": "14 Sep 2026", "Activity": "Irrigation review", "Crop": "Chilli", "Status": "Monitor"},
    ])
    st.dataframe(history, width="stretch", hide_index=True, column_config={
        "Status": st.column_config.TextColumn("Status", width="small"),
    })


def show_crop_recommendation(lang):
    st.header(t("nav_crop", lang))
    soil = st.selectbox(t("soil", lang), ["Black", "Red", "Sandy"])
    season = st.selectbox(t("season", lang), ["Kharif", "Rabi", "Zaid"])
    rain = st.number_input(t("rainfall", lang), min_value=0.0, max_value=10000.0, step=50.0)
    humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, step=5.0, value=50.0)
    temperature = st.number_input("Temperature (°C)", min_value=0.0, max_value=50.0, step=1.0, value=25.0)
    if st.button(t("recommend", lang)):
        try:
            result = recommend_crop(soil, season, rain, humidity, temperature)
            st.success(f"Recommended crop: **{result}**")
        except Exception as e:
            st.error(f"Error: {e}")


def show_disease_detection(lang):
    st.markdown('<div class="section-kicker">Plant health intelligence</div>', unsafe_allow_html=True)
    st.header("Crop health", icon=":material/health_and_safety:")
    st.caption("Upload a clear leaf photo for a cautious AI assessment. Results are guidance, not a laboratory diagnosis.")
    upload_left, upload_center, upload_right = st.columns([1, 2, 1])
    with upload_center:
        uploaded = st.file_uploader("Upload a leaf image", type=["jpg", "png", "jpeg"])
    if uploaded:
        img = PIL.Image.open(uploaded)
        preview, details = st.columns([1, 1])
        with preview:
            st.image(img, caption="Uploaded field image", width="stretch")
        with details:
            st.markdown("**Ready for analysis**")
            st.caption("Best results come from a well-lit image focused on one leaf.")
        if st.button("Analyze crop health", type="primary", icon=":material/biotech:"):
            with st.spinner("Analyzing..."):
                try:
                    result = predict_disease(img)
                    is_healthy = "healthy" in result["disease"].lower()
                    result_class = "health-good" if is_healthy else "health-risk"
                    st.markdown(
                        f"<div class='health-result {result_class}'><div class='result-label'>Prediction</div><div class='result-value'>{result['disease']}</div><div>Confidence: {result.get('confidence', 'Not available')}</div></div>",
                        unsafe_allow_html=True,
                    )
                    if result.get("observations"):
                        st.write(f"**Observations:** {result['observations']}")
                    st.info(f"Treatment: {result['treatment']}")
                except Exception as e:
                    st.error(f"Error: {e}")


def show_fertilizer(lang):
    st.header(t("nav_fertilizer", lang))
    n = st.number_input("Nitrogen (N)", min_value=0.0, value=0.0)
    p = st.number_input("Phosphorus (P)", min_value=0.0, value=0.0)
    k = st.number_input("Potassium (K)", min_value=0.0, value=0.0)
    if st.button("Get Recommendation"):
        try:
            advice = recommend_fertilizer(n, p, k)
            st.write(advice)
        except Exception as e:
            st.error(f"Error: {e}")


def show_soil_analysis():
    st.markdown('<div class="section-kicker">Field intelligence</div>', unsafe_allow_html=True)
    st.header("Soil analysis", icon=":material/landscape:")
    st.caption("Enter today’s field readings to get a simple soil-health signal.")
    with st.container(border=True):
        input_one, input_two, input_three = st.columns(3)
        with input_one:
            soil_moisture = st.number_input("Moisture (%)", 0.0, 100.0, 58.0, 1.0)
            soil_ph = st.number_input("pH", 0.0, 14.0, 6.8, 0.1)
        with input_two:
            nitrogen = st.number_input("Nitrogen (N)", 0.0, 500.0, 120.0, 5.0)
            phosphorus = st.number_input("Phosphorus (P)", 0.0, 500.0, 60.0, 5.0)
        with input_three:
            potassium = st.number_input("Potassium (K)", 0.0, 500.0, 60.0, 5.0)
            soil_temperature = st.number_input("Temperature (°C)", 0.0, 60.0, 28.0, 1.0)
        humidity = st.slider("Field humidity (%)", 0, 100, 62)

    if st.button("Analyze soil", type="primary", icon=":material/analytics:"):
        with st.spinner("Reading field conditions..."):
            score = 0
            score += 1 if 35 <= soil_moisture <= 75 else 0
            score += 1 if 6.0 <= soil_ph <= 7.8 else 0
            score += 1 if nitrogen >= 80 and phosphorus >= 35 and potassium >= 35 else 0
            score += 1 if 18 <= soil_temperature <= 35 else 0
            status = "Good" if score >= 4 else "Moderate" if score >= 2 else "Needs attention"
            color = "green" if score >= 4 else "orange" if score >= 2 else "red"
            st.markdown(f"<div class='result-box {color}'><div class='result-label'>Soil health</div><div class='result-value'>{status}</div><div>Score: {score}/4 · Confirm with a laboratory soil test before major fertilizer applications.</div></div>", unsafe_allow_html=True)


def show_recommendations():
    st.markdown('<div class="section-kicker">Decision support</div>', unsafe_allow_html=True)
    st.header("Recommendations", icon=":material/lightbulb:")
    st.caption("Practical next steps based on current field conditions and crop-health signals.")
    advice_one, advice_two, advice_three = st.columns(3)
    with advice_one:
        st.markdown("### :material/eco: Fertilizer")
        st.markdown("- Base application on soil-test values\n- Split nitrogen across crop stages\n- Avoid urea before heavy rain")
        st.caption("Always follow the local label and agriculture officer guidance.")
    with advice_two:
        st.markdown("### :material/water_drop: Irrigation")
        st.markdown("- Check root-zone moisture first\n- Irrigate during cooler hours\n- Use mulch to reduce evaporation")
        st.caption("Drip irrigation is useful where water is limited.")
    with advice_three:
        st.markdown("### :material/health_and_safety: Disease")
        st.markdown("- Scout leaves and stems weekly\n- Remove severely affected parts\n- Confirm the pest before spraying")
        st.caption("Upload a clear leaf image in Crop health for AI assessment.")


def show_alerts():
    st.markdown('<div class="section-kicker">Monitoring center</div>', unsafe_allow_html=True)
    st.header("Alerts", icon=":material/notifications:")
    st.caption("Signals that may need attention in the next field visit.")
    st.error("**Disease risk high**  \nInspect cotton squares and chilli flowers for visible pest activity.", icon=":material/report:")
    st.warning("**Moisture watch**  \nDo not irrigate until the root-zone moisture check is complete.", icon=":material/water_drop:")
    st.success("**Weather window open**  \nNo live rain alert is currently available. Check the local forecast before spraying.", icon=":material/check_circle:")


def show_weather(lang):
    st.header(t("nav_weather", lang))
    try:
        weather = fetch_weather()
        if weather:
            st.image(weather["icon"], width=80)
            st.metric("Temp", f"{weather['temp']} °C", weather["desc"])
            st.write(advice_from_weather(weather))
        else:
            st.error("Weather information unavailable.")
    except Exception as e:
        st.error(f"Weather error: {e}")


def show_market(lang):
    st.header(t("nav_market", lang))
    try:
        crops = available_crops()
        crop = st.selectbox("Choose crop", crops)
        price = get_current_price(crop)
        pred = predict_price_trend(crop)
        st.metric("Current Price", f"₹{price}/qtl")
        st.metric("Predicted Next Month", f"₹{pred:.2f}/qtl")
        chart = get_price_chart(crop)
        if chart:
            st.plotly_chart(chart, key="market_chart")
        # Table
        st.subheader("Price Table")
        import pandas as pd
        data = {"Crop": crops, "Price (₹/qtl)": [get_current_price(c) for c in crops]}
        df = pd.DataFrame(data)
        st.table(df)
    except Exception as e:
        st.error(f"Market error: {e}")


def show_schemes(lang):
    st.header(t("nav_schemes", lang))
    st.markdown("""
    - **PM-KISAN:** ₹6000/year to farmers for cultivation. Apply online at pmkisan.gov.in
    - **Rythu Bandhu:** Investment support for Telangana farmers, up to ₹8000/ha.
    - **PMFBY:** Crop insurance scheme covering yield loss. Premium as low as 2%.
    - **Kisan Credit Card:** Easy loans for farmers at low interest.
    (Visit local agriculture office or agmarknet.gov.in for details.)
    """)


def show_chat(lang):
    st.header("AI farming assistant", icon=":material/chat:")
    st.caption("Ask in English, Hindi, or Telugu. Type a question or use the microphone in the chat box.")

    if st.session_state.get("chat_schema_version") != 2:
        st.session_state.chat_schema_version = 2
        st.session_state.messages = []

    if not st.session_state.get("messages"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Namaste! I am KrishiSahay, your Telangana farming assistant.\n\nI can help with crop planning, pests, disease, fertilizer, weather, schemes, and market prices.",
            "timestamp": timestamp(),
        }]

    st.markdown('<div class="chat-thread">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        st.markdown(
            bubble_html(msg["role"], msg["content"], msg.get("timestamp", "")),
            unsafe_allow_html=True,
        )
    st.markdown('</div><div id="latest-message"></div>', unsafe_allow_html=True)
    st.html(
        """
        <script>
        const latestMessage = document.getElementById("latest-message");
        if (latestMessage) {
            latestMessage.scrollIntoView({behavior: "smooth", block: "end"});
        }
        </script>
        """,
        unsafe_allow_javascript=True,
    )

    submission = st.chat_input(
        "Ask about crops, pests, weather, or schemes...",
        accept_audio=True,
        key="farming_chat_input",
    )
    if not submission:
        return

    prompt = (getattr(submission, "text", "") or "").strip()
    audio = getattr(submission, "audio", None)
    if audio and not prompt:
        with st.spinner("Transcribing your question..."):
            try:
                prompt = transcribe_audio(audio)
            except Exception as error:
                st.error(f"I could not understand the recording. Please try again or type your question. ({error})")
                return

    if not prompt:
        st.warning("Please type a question or record a voice question first.")
        return

    user_message = {"role": "user", "content": prompt, "timestamp": timestamp()}
    st.session_state.messages.append(user_message)
    record_chat_message("user", prompt)

    with st.status("KrishiSahay is preparing a practical answer...", expanded=False) as status:
        answer = generate_response(prompt, st.session_state.messages[:-1], lang)
        status.update(label="Answer ready", state="complete")

    assistant_message = {"role": "assistant", "content": answer, "timestamp": timestamp()}
    st.session_state.messages.append(assistant_message)
    record_chat_message("assistant", answer)
    st.rerun()


# ─── Page config & farmer-friendly green theme ──────────────────────────────
st.set_page_config(
    page_title="KrishiSahay",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌾 KrishiSahay")
    st.caption("Telangana farmer intelligence")
    st.markdown("Crop planning  ·  Weather  ·  Markets  ·  Plant health")

    page = st.selectbox("Workspace", [
        "Dashboard", "Crop planning", "Crop health", "Soil analysis", "Recommendations", "Alerts",
        "Fertilizer guide", "Weather", "Market prices", "Government schemes", "AI assistant",
    ], index=0, label_visibility="collapsed")
    language = st.selectbox("Language", ["English", "Hindi", "Telugu"], index=0)

    if st.button("Clear chat history", icon=":material/delete_sweep:"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Built for Rathod Ajay · Lal Bahadur Nagar")

# Hero Section
st.markdown("""
<div class='hero'>
<h1>🌾 KrishiSahay</h1>
<p>Practical intelligence for every growing season</p>
<p>Plan crops, understand plant health, follow field conditions, and make better farm decisions from one calm workspace.</p>
</div>
""", unsafe_allow_html=True)

if page == "Dashboard":
    show_dashboard(language)
elif page == "Crop planning":
    show_crop_recommendation(language)
elif page == "Crop health":
    show_disease_detection(language)
elif page == "Soil analysis":
    show_soil_analysis()
elif page == "Recommendations":
    show_recommendations()
elif page == "Alerts":
    show_alerts()
elif page == "Fertilizer guide":
    show_fertilizer(language)
elif page == "Weather":
    show_weather(language)
elif page == "Market prices":
    show_market(language)
elif page == "Government schemes":
    show_schemes(language)
elif page == "AI assistant":
    show_chat(language)
