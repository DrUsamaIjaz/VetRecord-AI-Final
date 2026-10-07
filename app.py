import streamlit as st
from orchestrator import run_workflow
from voice import transcribe_audio
from database import save_record, load_records, create_share_link, get_shared_record

st.set_page_config(page_title="VetRecord AI v2", page_icon="🐾", layout="wide")
st.title("🐾 VetRecord AI")
st.caption("Multi-Agent Livestock Health Assistant — Urdu + English")

tab1, tab2, tab3, tab4 = st.tabs(
    ["🩺 Diagnose", "📚 History", "📊 Analytics", "🔗 Vet View"]
)

# ---------- TAB 1 ----------
with tab1:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 🎤 Voice Input (Urdu / English)")
        lang = st.radio("Voice language", ["ur", "en"], horizontal=True)
        audio_value = st.audio_input("Tap to record")

        user_input = st.text_area(
            "Or type here",
            placeholder="مثال: میرا کتا دو دن سے الٹیاں کر رہا ہے",
            height=100
        )

        if "record" not in st.session_state:
            st.session_state.record = None
        if "audio_text" not in st.session_state:
            st.session_state.audio_text = ""

        if audio_value:
            with st.spinner("Transcribing..."):
                try:
                    t = transcribe_audio(audio_value.getvalue(), language=lang)
                    st.session_state.audio_text = t
                    st.info(f"📝 {t}")
                except Exception as e:
                    st.error(f"Transcription failed: {e}")

        final_input = st.session_state.audio_text or user_input

        if st.button("🚀 Run Multi-Agent Workflow", type="primary", use_container_width=True):
            if not final_input.strip():
                st.warning("Record or type something first.")
            else:
                with st.spinner("Agents thinking..."):
                    st.session_state.record = run_workflow(final_input, language=lang)
                st.session_state.audio_text = ""

    with col_right:
        if st.session_state.record:
            rec = st.session_state.record

            st.markdown("### 🧠 Agent Workflow Trace")
            st.write("**1️⃣ Symptom Extractor** ✅")
            st.write("**2️⃣ Urgency Triage** ✅")
            st.write("**3️⃣ Record Writer** ✅")
            if rec.get("reminder"):
                st.write("**4️⃣ Reminder Agent** ✅ (triggered by urgency)")
            else:
                st.write("**4️⃣ Reminder Agent** ⏭️ skipped (low urgency)")

            st.divider()

            urgency = rec.get("urgency", "Medium")
            if urgency == "High":
                st.error("🚨 URGENT — Seek vet care immediately")
            elif urgency == "Medium":
                st.warning("⚠️ Moderate urgency")
            else:
                st.success("✅ Low urgency")

            st.markdown(f"**🐾 Animal:** {rec.get('pet_info','?')}")
            st.markdown(f"**⏱️ Duration:** {rec.get('duration','?')}")
            st.markdown(f"**🚨 Urgency:** {urgency}")

            st.markdown("**🤒 Symptoms:**")
            for s in rec.get("symptoms", []):
                st.write(f"• {s}")

            st.markdown("**🔍 Possible Conditions:**")
            for c in rec.get("possible_conditions", []):
                st.write(f"• {c}")

            st.markdown("**🩺 Next Steps:**")
            st.success(rec.get("recommended_next_steps", "Consult vet"))

            if rec.get("reminder"):
                st.markdown("**🔔 Auto-Scheduled Reminder:**")
                r = rec["reminder"]
                st.info(f"{r.get('vaccine','Follow-up')} due on {r.get('due_date','')}")

            if rec.get("vet_notification"):
                st.markdown("**📨 Vet Notification:**")
                st.info(rec["vet_notification"])

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("💾 Save", use_container_width=True):
                    if save_record(rec):
                        st.success("Saved!")
            with col_b:
                if st.button("🔗 Share with Vet", use_container_width=True):
                    sid = create_share_link(rec)
                    if sid:
                        st.success(f"Share ID: `{sid}`")

            with st.expander("📄 View Full State (JSON)"):
                st.json(rec)

# ---------- TAB 2 ----------
with tab2:
    st.markdown("### 📚 Saved Records")
    records = load_records()
    if not records:
        st.info("No records yet.")
    else:
        for i, r in enumerate(reversed(records), 1):
            with st.expander(f"#{len(records)-i+1} — {r.get('pet_info','?')} — {r.get('urgency','?')} — {r.get('timestamp','')}"):
                st.json(r)

# ---------- TAB 3 ----------
with tab3:
    st.markdown("### 📊 Analytics")
    records = load_records()
    if not records:
        st.info("No data yet.")
    else:
        high = sum(1 for r in records if r.get("urgency") == "High")
        med = sum(1 for r in records if r.get("urgency") == "Medium")
        low = sum(1 for r in records if r.get("urgency") == "Low")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", len(records))
        c2.metric("🚨 High", high)
        c3.metric("⚠️ Medium", med)
        c4.metric("✅ Low", low)
        species = {}
        for r in records:
            s = r.get("pet_info", "Unknown").lower()
            species[s] = species.get(s, 0) + 1
        st.bar_chart(species)

# ---------- TAB 4 ----------
with tab4:
    st.markdown("### 🔗 Vet Access")
    sid = st.text_input("Share ID").strip()
    if sid:
        rec = get_shared_record(sid)
        if rec:
            st.success("Record found")
            st.json(rec)
        else:
            st.error("Not found")