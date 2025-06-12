# -*- coding: utf-8 -*-
"""
Global Warming Generative Art - Headless Image Generator

This script fetches global temperature anomaly data from the global-warming.org API
and visualizes it as a static, horizontal wave, saving it as a PNG image.

This version is designed to run in a headless environment (like a GitHub Action)
and uses the Pillow library instead of turtle for image generation.
"""

import requests
import colorsys
import sys
from PIL import Image, ImageDraw

# --- Configuration ---
API_URL = "https://global-warming.org/api/temperature-api"
WAVE_AMPLITUDE_SCALE = 200
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 800
OUTPUT_FILENAME = "temperature_wave.png"

def fetch_temperature_data():
    """Fetches temperature data from the API."""
    print("Fetching temperature data from the API...")
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        print("Data fetched successfully.")
        return response.json().get('result', [])
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch data from API: {e}", file=sys.stderr)
        return None
    except ValueError:
        print("Error: Could not decode JSON from API response.", file=sys.stderr)
        return None

def get_color_from_temperature(temp, min_temp, max_temp):
    """Maps a temperature value to a color from blue (cold) to red (hot)."""
    normalized_temp = (temp - min_temp) / (max_temp - min_temp)
    hue = 0.66 - (normalized_temp * 0.66)
    r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 0.95)
    # Convert to 0-255 scale for Pillow
    return (int(r * 255), int(g * 255), int(b * 255))
    
def draw_visualization(data):
    """Draws the static wave visualization and saves it to a file."""
    if not data:
        print("No data available to visualize.", file=sys.stderr)
        return

    # --- 1. Data Processing ---
    valid_data = []
    for entry in data:
        try:
            temp = float(entry['station'])
            time = float(entry['time'])
            valid_data.append({'time': time, 'temp': temp})
        except (ValueError, KeyError):
            continue
    
    if not valid_data:
        print("Filtered data is empty. Cannot visualize.", file=sys.stderr)
        return

    temps = [d['temp'] for d in valid_data]
    min_temp, max_temp = min(temps), max(temps)

    # --- 2. Setup Drawing Environment ---
    # Create a new black image
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), "black")
    draw = ImageDraw.Draw(image)
    
    # --- 3. Draw the Data Points ---
    print(f"Drawing {len(valid_data)} data points...")

    x_start = 50
    x_end = IMAGE_WIDTH - 50
    x_range = x_end - x_start

    # Draw the center line for 0.0 anomaly
    center_y = IMAGE_HEIGHT / 2
    draw.line([(x_start, center_y), (x_end, center_y)], fill="gray", width=1)

    for i, point in enumerate(valid_data):
        current_temp = point['temp']
        
        # X position is chronological
        x = x_start + (i / len(valid_data)) * x_range
        # Y position is the temp anomaly, centered vertically
        y = center_y - (current_temp * WAVE_AMPLITUDE_SCALE)
        
        color = get_color_from_temperature(current_temp, min_temp, max_temp)
        dot_size = 4 + abs(current_temp) * 3
        
        # Define the bounding box for the dot (ellipse)
        bbox = [x - dot_size, y - dot_size, x + dot_size, y + dot_size]
        draw.ellipse(bbox, fill=color)

    # --- 4. Finalize and Save Image ---
    print(f"Saving image to {OUTPUT_FILENAME}...")
    image.save(OUTPUT_FILENAME)
    print("Visualization complete.")

def main():
    """Main function to run the script."""
    data = fetch_temperature_data()
    if data:
        draw_visualization(data)
    else:
        print("Exiting due to data fetching error.")

if __name__ == "__main__":
    main()
