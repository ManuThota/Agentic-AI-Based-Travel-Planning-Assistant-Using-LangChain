import os
import sys
import traceback
sys.path.append(os.getcwd())

from app import create_pdf_document

def test_pdf():
    print("Testing PDF creation...")
    dummy_trip = {
        "trip_summary": {
            "destination": "Goa",
            "source": "Delhi",
            "duration": "3 Days, 2 Nights",
            "dates": "May 28 - May 30"
        },
        "flight_selected": {
            "flight_number": "6E-501",
            "airline": "IndiGo",
            "price": 4800,
            "departure_time": "06:15",
            "arrival_time": "08:55",
            "duration": "2h 40m",
            "class": "Economy"
        },
        "hotel_selected": {
            "hotel_name": "Novotel Goa",
            "price_per_night": 3000,
            "rating": 4.5,
            "amenities": ["Pool", "Free WiFi"],
            "total_hotel_cost": 6000
        },
        "day_wise_itinerary": [
            {
                "day": 1,
                "weather": "Clear Sky (Temp: 25C to 30C)",
                "activities": [
                    {
                        "time": "Morning",
                        "place": "Calangute Beach",
                        "description": "Relax on the beach"
                    }
                ]
            }
        ],
        "budget_breakdown": {
            "flight": 4800,
            "accommodation": 6000,
            "food_and_local_transport": 3000,
            "total_estimated_budget": 13800
        },
        "reasoning": "Indigo is the cheapest and Novotel has good ratings."
    }
    
    try:
        pdf_bytes = create_pdf_document(dummy_trip, "Dummy MD")
        print("PDF generated successfully! Type:", type(pdf_bytes), "Length:", len(pdf_bytes))
    except Exception as e:
        print("PDF generation failed:")
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf()
