# Vagabond AI: Agentic Travel Planning Assistant Using LangChain

Vagabond AI is an intelligent, autonomous travel planner built using Python, LangChain, and Streamlit. It leverages an Agentic AI workflow to design personalized multi-day itineraries, recommending optimal flights, hotels, and attractions, fetching real-time weather forecasts, and providing interactive budget breakdowns.

---

## 🌟 Key Features

1. **Groq Llama Models**: High-performance execution powered by Llama models hosted on Groq.
2. **Autonomous ReAct Agent**: Orchestrated with LangChain using tool-calling paradigms. The agent reasons through the query, queries data, adjusts decisions dynamically based on budget constraints, and compiles the response.
3. **5 Specialized Data Tools**:
   * **Flight Finder**: Simulates flights by origin/destination and cabin class, sorting by price or duration.
   * **Hotel Selector**: Recommends hotel accommodations based on destination, pricing, ratings, and amenities using keyless OpenStreetMap Nominatim searches.
   * **Attraction Explorer**: Suggests point-of-interest (POI) sights matching user's custom travel styles (Beach, Heritage, Nature, Adventure).
   * **Live Weather Reporter**: Connects to the free **Open-Meteo API** to get real-time 7-day weather forecasts for any city in the world using dynamic geocoding.
   * **Budget Estimator**: Sums and itemizes travel costs (flights, accommodations, food, transit, entry fees).
4. **Premium Streamlit UI**: A high-end glassmorphic dark-themed dashboard featuring interactive controls, day-wise timeline views, custom visual cards, and responsive states.
5. **Interactive Budget Visualization**: Interactive Plotly distribution chart depicting trip expenses.
6. **PDF Export**: Instantly compile and download the generated travel itinerary as a styled PDF report.

---

## ⚡ Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your machine.

### 2. Clone or Copy the Repository
Place the files into your working directory:
```bash
cd "C:\Users\pandu\Desktop\Agentic AI-Based Travel Planning Assistant Using LangChain"
```

### 3. Install Dependencies
Run pip to install all requirements:
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Copy the example environment configuration and fill in your API key:
```bash
copy .env.example .env
```
Open `.env` and configure your keys:
```env
# For Groq AI
GROQ_API_KEY=gsk_...
```
*Note: You can obtain a Groq API key from console.groq.com.*

---

## 🚀 Running the Application

### 💻 Launch the Streamlit Web UI
Run the Streamlit server:
```bash
python -m streamlit run app.py
```
This will start the local server and automatically open a web browser tab at `http://localhost:8501`.
