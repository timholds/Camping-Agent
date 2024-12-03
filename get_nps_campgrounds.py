from dotenv import load_dotenv
import os
import requests
from rich.console import Console
from rich.table import Table
import pdb
# Load environment variables
load_dotenv()
API_KEY = os.getenv('NPS_API_KEY')

if not API_KEY:
    raise ValueError("Please set NPS_API_KEY in your .env file")

def fetch_all_campgrounds():
    """Fetch all campgrounds across all states"""
    base_url = "https://developer.nps.gov/api/v1/campgrounds"
    
    params = {
        "api_key": API_KEY,
        "limit": 50
    }
    
    all_campgrounds = []
    start = 0
    
    console = Console()
    console.print("Fetching campgrounds...", style="bold blue")
    
    while True:
        params["start"] = start
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        current_campgrounds = data["data"]
        
        if not current_campgrounds or start == 100:
            break
            
        all_campgrounds.extend(current_campgrounds)
        start += 50
        console.print(f"Fetched {len(all_campgrounds)} campgrounds...", style="dim")
    
    return all_campgrounds

def get_state_code(campground):
    """Safely extract state code from campground data"""
    addresses = campground.get('addresses', [])
    if addresses and len(addresses) > 0:
        return addresses[0].get('stateCode', 'N/A')
    return 'N/A'

def display_campgrounds(campgrounds):
    """Display campgrounds in a formatted table"""
    console = Console()
    
    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="dim", width=30)
    table.add_column("Park", style="dim", width=30)
    table.add_column("State", style="dim", width=10)
    table.add_column("Sites", justify="right", width=10)
    table.add_column("Reservable", width=10)
    
    # Add rows
    for camp in campgrounds:
        print(type(camp))
        pdb.set_trace()
        table.add_row(
            camp.get('name', 'N/A'),
            camp.get('parkName', 'N/A'),
            get_state_code(camp),
            str(camp.get('totalSites', 'N/A')),
            '✓' if camp.get('reservationInfo', {}).get('reservable', False) else '✗'
        )
    
    # Print summary and table
    console.print(f"\nFound {len(campgrounds)} campgrounds:", style="bold green")
    console.print(table)
    
    # Print additional statistics
    states = set(get_state_code(camp) for camp in campgrounds)
    reservable = sum(1 for camp in campgrounds 
                    if camp.get('reservationInfo', {}).get('reservable', False))
    
    console.print("\nStatistics:", style="bold blue")
    console.print(f"Total states: {len(states)}")
    console.print(f"Reservable campgrounds: {reservable} ({reservable/len(campgrounds)*100:.1f}%)")

if __name__ == "__main__":
    try:
        campgrounds = fetch_all_campgrounds()
        display_campgrounds(campgrounds)
        
    except requests.exceptions.RequestException as e:
        console = Console()
        console.print(f"Error fetching data: {e}", style="bold red")