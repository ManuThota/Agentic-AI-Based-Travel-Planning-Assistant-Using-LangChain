import streamlit as st
import datetime
import json
import os
import io
import plotly.express as px
import pandas as pd
from fpdf import FPDF

# Configure Streamlit page layout and title
st.set_page_config(
    page_title="Vagabond AI - Agentic Travel Planner",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS for styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Global font override */
    html, body, [class*="css"], .stText, .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main container background */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161b22 100%);
        color: #f0f6fc;
    }
    
    /* Banner Title */
    .banner-title {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }
    .banner-subtitle {
        color: #8b949e;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Premium Styled Cards with smooth floating animations */
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-4px) scale(1.005);
        border-color: #4facfe;
        box-shadow: 0 10px 25px rgba(79, 172, 254, 0.15);
    }
    
    .day-card {
        border-left: 5px solid #f2cc60 !important;
        transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .day-card:hover {
        transform: translateY(-4px) scale(1.005);
        border-color: #f2cc60 !important;
        box-shadow: 0 10px 25px rgba(242, 204, 96, 0.15) !important;
    }
    .day-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(48, 54, 61, 0.4);
        padding-bottom: 8px;
        margin-bottom: 15px;
    }
    .day-card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f2cc60;
    }
    .day-card-weather {
        font-size: 0.85rem;
        color: #c9d1d9;
        background: rgba(242, 204, 96, 0.1);
        border: 1px solid rgba(242, 204, 96, 0.2);
        padding: 2px 10px;
        border-radius: 20px;
    }
    
    .flight-card {
        border-left: 5px solid #00f2fe;
    }
    .hotel-card {
        border-left: 5px solid #4facfe;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #58a6ff;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #58a6ff;
    }
    
    .badge {
        background: rgba(88, 166, 255, 0.15);
        color: #58a6ff;
        border: 1px solid rgba(88, 166, 255, 0.3);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .day-weather {
        background: rgba(48, 54, 61, 0.3);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.9rem;
        color: #c9d1d9;
        margin-bottom: 15px;
        border-left: 3px solid #f2cc60;
    }
    
    /* Timeline styling */
    .timeline-item {
        border-left: 2px solid #30363d;
        padding-left: 15px;
        position: relative;
        margin-bottom: 15px;
    }
    .timeline-time {
        font-weight: 600;
        color: #58a6ff;
        font-size: 0.9rem;
    }
    .timeline-title {
        font-weight: 600;
        font-size: 1.05rem;
        color: #f0f6fc;
    }
    .timeline-desc {
        color: #8b949e;
        font-size: 0.9rem;
    }
    
    /* Reduce space above the sidebar (left side) and move content to the very top */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    [data-testid="stSidebar"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.5rem !important;
        margin-top: 0rem !important;
    }
    div[data-testid="stSidebar"] div[class*="st-emotion-cache"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    /* Hide the top sidebar header spacing completely (contains the collapse arrow, pushes elements down) */
    [data-testid="stSidebarHeader"], .stSidebarHeader, div[class*="stSidebarHeader"] {
        display: none !important;
    }
    /* Reset browser margins for headers in sidebar (e.g. h3 elements) */
    [data-testid="stSidebar"] h3 {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Reduce space in the main content area (right side) and move content to the very top */
    .block-container, [data-testid="stAppViewBlockContainer"] {
        padding-top: 0.5rem !important;
        margin-top: 0rem !important;
    }
    
    /* Hide the top Streamlit header (contains Deploy button and 3-dot settings menu) */
    [data-testid="stHeader"] {
        display: none !important;
    }
    /* Hide the footer as well */
    footer {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Imports from agent module
import importlib
import agent.travel_agent
import tools.flight_tool
import tools.hotel_tool
import tools.places_tool

importlib.reload(agent.travel_agent)
importlib.reload(tools.flight_tool)
importlib.reload(tools.hotel_tool)
importlib.reload(tools.places_tool)

from agent.travel_agent import get_travel_agent_executor, parse_agent_response

class TravelItineraryPDF(FPDF):
    """Class to construct a clean PDF document for travel plans."""
    def header(self):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(79, 172, 254) # Blue accent
        self.cell(0, 10, 'VAGABOND AI - TRIP ITINERARY', border=False, new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_draw_color(48, 54, 61)
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(139, 148, 158)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} - Generated by Vagabond AI Travel Agent', align='C')

def create_pdf_document(trip_data: dict, md_text: str) -> bytes:
    """Generates PDF binary stream from the itinerary data."""
    pdf = TravelItineraryPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # 1. Summary
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(240, 246, 252)
    summary = trip_data.get("trip_summary", {})
    pdf.cell(0, 10, f"Trip to {summary.get('destination', 'Destination')}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 7, f"Origin: {summary.get('source', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Dates: {summary.get('dates', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Duration: {summary.get('duration', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 2. Flight & Hotel details
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "Flight Selection", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    flight = trip_data.get("flight_selected", {})
    if flight:
        pdf.cell(0, 6, f"Airline: {flight.get('airline', 'N/A')} ({flight.get('flight_number', 'N/A')})", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Schedule: Departs {flight.get('departure_time', 'N/A')} | Arrives {flight.get('arrival_time', 'N/A')} | Duration {flight.get('duration', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Class: {flight.get('class', 'N/A')} | Price: INR {flight.get('price', 0):,}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, "No flight details listed.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "Accommodation Details", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    hotel = trip_data.get("hotel_selected", {})
    if hotel:
        pdf.cell(0, 6, f"Hotel: {hotel.get('hotel_name', 'N/A')} ({hotel.get('rating', 'N/A')} Stars)", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Rate: INR {hotel.get('price_per_night', 0):,}/night | Total Cost: INR {hotel.get('total_hotel_cost', 0):,}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Amenities: {', '.join(hotel.get('amenities', []))}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, "No hotel details listed.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 3. Budget Summary
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "Estimated Budget Breakdown", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    budget = trip_data.get("budget_breakdown", {})
    for k, v in budget.items():
        label = k.replace("_", " ").title()
        pdf.cell(0, 6, f"{label}: INR {v:,}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 4. Day-Wise Plan
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "Day-by-Day Schedule", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    itinerary_days = trip_data.get("day_wise_itinerary", [])
    for day in itinerary_days:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, f"Day {day.get('day', 1)} - Weather: {day.get('weather', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 10)
        for act in day.get("activities", []):
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(30, 6, f"[{act.get('time', 'Slot')}]: ")
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 6, f"{act.get('place', 'Sight')} - {act.get('description', '')}")
            pdf.ln(1)
        pdf.ln(3)
        
    return bytes(pdf.output())

# Application Title Header
st.markdown('<div class="banner-title">Vagabond AI</div>', unsafe_allow_html=True)

# ----------------- SIDEBAR SETTINGS -----------------
st.sidebar.markdown("### Trip Settings")

# 1. Source and Destination inputs
source = st.sidebar.text_input("Source City", "Delhi", placeholder="Origin City")
destination = st.sidebar.text_input("Destination City", "Goa", placeholder="Destination City")

# 2. Date ranges
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
col_start, col_end = st.sidebar.columns(2)
with col_start:
    start_date = st.date_input("Start Date", today, min_value=today)
with col_end:
    end_date = st.date_input("End Date", today + datetime.timedelta(days=3), min_value=start_date)

# Calculate duration variables
days = (end_date - start_date).days + 1
nights = days - 1 if days > 1 else 0

# 3. Travel Preferences
budget_cap = st.sidebar.slider("Budget Limit (INR)", min_value=5000, max_value=150000, value=30000, step=5000)
flight_class = st.sidebar.selectbox("Cabin Class", ["Economy", "Business"])
travel_style = st.sidebar.multiselect(
    "Interests", 
    ["Heritage", "Beach", "Nature", "Adventure", "Shopping", "Relaxing"],
    default=["Beach", "Heritage"]
)


# ----------------- MAIN ACTION RENDERER -----------------
custom_prompt = st.text_area(
    "Custom Preferences",
    "Suggest the cheapest flight and a highly rated hotel. Plan a balanced, relaxed vacation.",
    height=80
)

# Plan Trip button
trigger_plan = st.button("Plan My Dream Trip", width="stretch")

if trigger_plan:
    if not source or not destination:
        st.error("Please fill in both the Source City and Destination City.")
    elif start_date > end_date:
        st.error("End Date must be after or equal to Start Date.")
    else:
        # Construct the detailed query for the LangChain agent
        style_str = ", ".join(travel_style) if travel_style else "balanced"
        query = (
            f"I want to plan a trip from '{source}' to '{destination}' starting from {start_date} to {end_date}. "
            f"This is a {days} days, {nights} nights trip. "
            f"My maximum budget limit is INR {budget_cap}. "
            f"My flight class preference is {flight_class}. "
            f"I prefer activities and places matching these styles: {style_str}. "
            f"Specific preferences: {custom_prompt}."
        )
        
        # Execute the agent runner inside a Streamlit spinner
        with st.spinner("Planning your trip..."):
            try:
                executor = get_travel_agent_executor()
                response = executor.invoke({"input": query})
                agent_output = response.get("output", "")
                
                # Parse the agent response to extract structured JSON and readable markdown
                parsed_json, markdown_text = parse_agent_response(agent_output)
                
                # Store in session state to persist findings
                st.session_state["trip_json"] = parsed_json
                st.session_state["trip_md"] = markdown_text
                st.success("Trip planned successfully!")
            except Exception as e:
                st.error(f"Error during planning execution: {e}")
                st.exception(e)

# Render results if available in session state
if "trip_json" in st.session_state and st.session_state["trip_json"]:
    trip_data = st.session_state["trip_json"]
    md_content = st.session_state["trip_md"]
    
    summary = trip_data.get("trip_summary", {})
    flight = trip_data.get("flight_selected", {})
    hotel = trip_data.get("hotel_selected", {})
    itinerary = trip_data.get("day_wise_itinerary", [])
    budget = trip_data.get("budget_breakdown", {})
    reasoning = trip_data.get("reasoning", "")
    
    # ----------------- Tabbed Presentation -----------------
    tab_dashboard, tab_raw_md, tab_json = st.tabs(["Premium Travel Dashboard", "Narrative Plan", "Raw JSON Data"])
    
    with tab_dashboard:
        # Trip Overview Header Panel
        st.markdown(f"""
        <div class="glass-card" style="background: linear-gradient(135deg, rgba(79,172,254,0.15) 0%, rgba(0,242,254,0.05) 100%);">
            <h2 style='margin: 0; color: #58a6ff;'>{summary.get('destination', 'Goa')} Vacation</h2>
            <p style='margin: 5px 0 0 0; color: #8b949e; font-size: 1.1rem;'>
                Departing from <b>{summary.get('source', 'Delhi')}</b> | <b>{summary.get('dates', '')}</b> ({summary.get('duration', '')})
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_transport, col_stay = st.columns(2)
        
        with col_transport:
            # Flight card
            st.markdown("<div class='glass-card flight-card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>Selected Flight</div>", unsafe_allow_html=True)
            if flight:
                st.markdown(f"""
                <h3 style='margin: 0; color: #f0f6fc;'>{flight.get('airline', 'N/A')}</h3>
                <span class='badge'>{flight.get('flight_number', 'N/A')}</span>
                <span class='badge'>{flight.get('class', 'Economy')} Class</span>
                <div style='margin-top: 15px; display: flex; justify-content: space-between; color: #c9d1d9;'>
                    <div>
                        <div style='font-size: 0.8rem; color: #8b949e;'>DEPARTURE</div>
                        <b>{flight.get('departure_time', 'N/A')}</b>
                    </div>
                    <div>
                        <div style='font-size: 0.8rem; color: #8b949e;'>DURATION</div>
                        <b>{flight.get('duration', 'N/A')}</b>
                    </div>
                    <div>
                        <div style='font-size: 0.8rem; color: #8b949e;'>ARRIVAL</div>
                        <b>{flight.get('arrival_time', 'N/A')}</b>
                    </div>
                </div>
                <hr style='border-color: #30363d; margin: 15px 0 10px 0;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='color: #8b949e;'>Flight Cost</span>
                    <span class='metric-value'>₹{flight.get('price', 0):,}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write("No flight selected.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_stay:
            # Hotel Card
            st.markdown("<div class='glass-card hotel-card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>Accommodation</div>", unsafe_allow_html=True)
            if hotel:
                # Format star ratings as icons
                rating_val = hotel.get('rating', 0.0)
                rating_desc = f"{rating_val} out of 5.0 Rating"
                
                amenities_badges = "".join([f"<span class='badge'>{a}</span>" for a in hotel.get("amenities", [])])
                
                st.markdown(f"""
                <h3 style='margin: 0; color: #f0f6fc;'>{hotel.get('hotel_name', 'N/A')}</h3>
                <div style='margin: 5px 0 10px 0; font-size: 0.9rem; color: #f2cc60;'>
                    {rating_desc}
                </div>
                <div style='margin-bottom: 15px;'>
                    {amenities_badges}
                </div>
                <hr style='border-color: #30363d; margin: 10px 0 10px 0;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='color: #8b949e;'>Nightly Rate (x{hotel.get('total_hotel_cost', 0) // max(1, hotel.get('price_per_night', 1))} nights)</span>
                    <span class='metric-value'>₹{hotel.get('total_hotel_cost', 0):,}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write("No hotel recommended.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Day-by-Day Schedule and weather forecast
        st.markdown("### Day-Wise Itinerary")
        
        # Render days 2 per row
        for i in range(0, len(itinerary), 2):
            cols = st.columns(2)
            for col_idx in range(2):
                if i + col_idx < len(itinerary):
                    day = itinerary[i + col_idx]
                    day_num = day.get("day", i + col_idx + 1)
                    weather_desc = day.get("weather", "Weather forecast unavailable")
                    
                    activities_html = ""
                    for act in day.get("activities", []):
                        time_val = act.get('time', 'Time')
                        place_val = act.get('place', 'POI')
                        desc_val = act.get('description', '')
                        activities_html += f'<div class="timeline-item"><div class="timeline-time">{time_val}</div><div class="timeline-title">{place_val}</div><div class="timeline-desc">{desc_val}</div></div>'
                        
                    day_card_html = f'<div class="glass-card day-card" style="height: 100%;"><div class="day-card-header"><span class="day-card-title">Day {day_num}</span><span class="day-card-weather">Weather: {weather_desc}</span></div><div class="day-card-body">{activities_html}</div></div>'
                    
                    with cols[col_idx]:
                        st.markdown(day_card_html, unsafe_allow_html=True)
                    
        # Budget section and reasoning
        st.markdown("### Cost & Recommendation Details")
        col_budget_data, col_budget_chart = st.columns([1, 1])
        
        with col_budget_data:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>Cost Breakdown</div>", unsafe_allow_html=True)
            
            df_costs = []
            for item, cost in budget.items():
                if item != "total_estimated_budget":
                    label = item.replace("_", " ").title()
                    st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 1rem;'>
                        <span style='color: #8b949e;'>{label}</span>
                        <b style='color: #c9d1d9;'>₹{cost:,}</b>
                    </div>
                    """, unsafe_allow_html=True)
                    df_costs.append({"Item": label, "Cost": cost})
                    
            st.markdown("<hr style='border-color: #30363d; margin: 15px 0 10px 0;'>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <b style='font-size: 1.2rem; color: #58a6ff;'>Total Project Budget</b>
                <span class='metric-value' style='color: #56d364;'>₹{budget.get('total_estimated_budget', budget.get('total_cost', 0)):,}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Decision Reasoning block
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>Choice Reasonings & Explanations</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #c9d1d9; font-size: 0.95rem; line-height: 1.5;'>{reasoning}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_budget_chart:
            st.markdown("<div class='glass-card' style='height: 100%; display: flex; align-items: center; justify-content: center;'>", unsafe_allow_html=True)
            if df_costs:
                df = pd.DataFrame(df_costs)
                fig = px.pie(
                    df, 
                    values='Cost', 
                    names='Item', 
                    title='Trip Cost Distribution (INR)',
                    color_discrete_sequence=px.colors.sequential.Tealgrn,
                    hole=0.4
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f0f6fc',
                    title_font_family='Outfit',
                    title_font_size=16,
                    margin=dict(t=40, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, width='stretch')
            st.markdown("</div>", unsafe_allow_html=True)
            
        # PDF Generation Button
        try:
            pdf_bytes = create_pdf_document(trip_data, md_content)
            st.download_button(
                label="Download PDF Report",
                data=bytes(pdf_bytes),
                file_name=f"itinerary_{summary.get('destination', 'trip').lower()}.pdf",
                mime="application/pdf",
                width="stretch"
            )
        except Exception as e:
            st.warning(f"Could not build PDF generator: {e}")
            
    with tab_raw_md:
        st.markdown(md_content)
        
    with tab_json:
        st.json(trip_data)
elif "trip_md" in st.session_state and st.session_state["trip_md"]:
    st.warning("The travel assistant generated the plan, but it could not be formatted into the structured dashboard. Showing the full narrative itinerary below:")
    st.markdown(st.session_state["trip_md"])
else:
    st.info("Set your criteria on the sidebar and click 'Plan My Dream Trip' to begin.")
