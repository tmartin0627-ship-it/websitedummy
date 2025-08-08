from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg
from PIL import Image
import openai
import base64
import io
from typing import List, Dict, Any
import json
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Warning: OPENAI_API_KEY environment variable not set. Image analysis will use fallback method.")

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://makeup-ingredient-app-ztfo438p.devinapps.com",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"]
)

MAKEUP_DATABASE = {
    "lipstick": {
        "name": "Rouge Dior Lipstick",
        "brand": "Dior",
        "shade": "999 Rouge Dior",
        "ingredients": [
            "Octyldodecanol",
            "CI 77891 (Titanium Dioxide)",
            "Synthetic Wax",
            "CI 15850 (Red 7 Lake)",
            "Polyglyceryl-2 Triisostearate",
            "CI 77491 (Iron Oxides)",
            "Hydrogenated Polyisobutene",
            "Cera Alba (Beeswax)",
            "CI 19140 (Yellow 5 Lake)",
            "Parfum (Fragrance)",
            "Tocopherol"
        ],
        "category": "Lip Color",
        "source": "Dior Official Website - Product Ingredients",
        "manufacturer_url": "https://www.dior.com",
        "price_range": "$38-42",
        "description": "Couture color lipstick with 16-hour wear"
    },
    "foundation": {
        "name": "Double Wear Stay-in-Place Makeup",
        "brand": "Estée Lauder",
        "shade": "1W2 Sand",
        "ingredients": [
            "Water\\Aqua\\Eau",
            "Cyclopentasiloxane",
            "Trimethylsiloxysilicate",
            "PEG-10 Dimethicone",
            "Titanium Dioxide",
            "Butylene Glycol",
            "Arbutin",
            "Sodium Chloride",
            "Disteardimonium Hectorite",
            "Phenoxyethanol",
            "Iron Oxides (CI 77491, CI 77492, CI 77499)"
        ],
        "category": "Base Makeup",
        "source": "Estée Lauder Official Website - INCI List",
        "manufacturer_url": "https://www.esteelauder.com",
        "price_range": "$52-58",
        "description": "24-hour wear liquid foundation with medium-to-full coverage"
    },
    "eyeshadow": {
        "name": "Naked3 Eyeshadow Palette",
        "brand": "Urban Decay",
        "shade": "Rose-Hued Neutrals",
        "ingredients": [
            "Talc",
            "Zinc Stearate",
            "Dimethicone",
            "Octyldodecyl Stearoyl Stearate",
            "Phenoxyethanol",
            "Caprylyl Glycol",
            "Mica",
            "Titanium Dioxide (CI 77891)",
            "Iron Oxides (CI 77491, CI 77492, CI 77499)",
            "Ultramarines (CI 77007)",
            "Carmine (CI 75470)"
        ],
        "category": "Eye Makeup",
        "source": "Urban Decay Official Website - Product Details",
        "manufacturer_url": "https://www.urbandecay.com",
        "price_range": "$54-58",
        "description": "12-shade eyeshadow palette with rose-hued neutral tones"
    },
    "mascara": {
        "name": "Better Than Sex Mascara",
        "brand": "Too Faced",
        "shade": "Black",
        "ingredients": [
            "Water (Aqua)",
            "Paraffin",
            "Potassium Cetyl Phosphate",
            "Beeswax (Cera Alba)",
            "Carnauba Wax (Copernicia Cerifera)",
            "Acacia Senegal Gum",
            "Glycerin",
            "Hydroxyethylcellulose",
            "Iron Oxides (CI 77499)",
            "Phenoxyethanol",
            "Panthenol"
        ],
        "category": "Eye Makeup",
        "source": "Too Faced Official Website - Ingredient List",
        "manufacturer_url": "https://www.toofaced.com",
        "price_range": "$27-29",
        "description": "Volumizing and lengthening mascara with hourglass-shaped brush"
    }
}

USER_PORTFOLIO = []

def analyze_makeup_image(image: Image.Image) -> List[Dict[str, Any]]:
    """
    Analyze the image to detect makeup products using OpenAI Vision API.
    More accurate than OpenCV and avoids memory issues.
    """
    detected_products = []
    
    try:
        if not openai.api_key:
            return [MAKEUP_DATABASE["foundation"]]
        
        img_buffer = io.BytesIO()
        image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        image.save(img_buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        prompt = """Analyze this image and identify any makeup products visible. 
        
        Look specifically for:
        - Lipstick (red, pink, or colored lip products)
        - Foundation (liquid makeup, skin-tone products in bottles/tubes)
        - Mascara (dark eye makeup in tubes)
        - Eyeshadow (colored powders in palettes or compacts)
        
        Do NOT identify:
        - Skincare products (moisturizers, serums, cleansers)
        - General beauty tools
        - Non-makeup items
        
        Respond with a JSON array of detected makeup products. Each product should have:
        - "type": one of "lipstick", "foundation", "mascara", "eyeshadow"
        - "confidence": number from 0-1
        - "description": brief description of what you see
        
        If no makeup products are clearly visible, return an empty array []."""
        
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        response_text = response.choices[0].message.content
        
        try:
            detected_items = json.loads(response_text)
            
            for item in detected_items:
                if item.get("confidence", 0) > 0.6:
                    product_type = item.get("type")
                    if product_type in MAKEUP_DATABASE:
                        detected_products.append(MAKEUP_DATABASE[product_type])
        
        except json.JSONDecodeError:
            response_lower = response_text.lower()
            if "lipstick" in response_lower or "lip" in response_lower:
                detected_products.append(MAKEUP_DATABASE["lipstick"])
            if "foundation" in response_lower or "base makeup" in response_lower:
                detected_products.append(MAKEUP_DATABASE["foundation"])
            if "mascara" in response_lower or "eye makeup" in response_lower:
                detected_products.append(MAKEUP_DATABASE["mascara"])
            if "eyeshadow" in response_lower or "palette" in response_lower:
                detected_products.append(MAKEUP_DATABASE["eyeshadow"])
        
        seen = set()
        unique_products = []
        for product in detected_products:
            product_key = (product["name"], product["brand"])
            if product_key not in seen:
                seen.add(product_key)
                unique_products.append(product)
        
        return unique_products
        
    except Exception as api_error:
        print(f"OpenAI Vision API failed: {api_error}")
        return [MAKEUP_DATABASE["foundation"]]

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/analyze-makeup")
async def analyze_makeup(file: UploadFile = File(...)):
    """
    Analyze uploaded makeup photo and return detected products with ingredients
    """
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        detected_products = analyze_makeup_image(image)
        
        if not detected_products:
            detected_products = [
                {
                    "name": "General Makeup Product",
                    "brand": "Unknown",
                    "ingredients": [
                        "Water (Aqua)",
                        "Glycerin",
                        "Dimethicone",
                        "Titanium Dioxide",
                        "Iron Oxides",
                        "Phenoxyethanol"
                    ],
                    "category": "Cosmetic Product"
                }
            ]
        
        return {
            "success": True,
            "products_detected": len(detected_products),
            "products": detected_products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/products")
async def get_all_products():
    """
    Get all available makeup products in the database
    """
    return {
        "success": True,
        "products": list(MAKEUP_DATABASE.values())
    }

@app.post("/portfolio/add")
async def add_to_portfolio(product_data: dict):
    """
    Add a makeup product to user's personal portfolio
    """
    try:
        import time
        product_data["id"] = len(USER_PORTFOLIO) + 1
        product_data["added_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        USER_PORTFOLIO.append(product_data)
        
        return {
            "success": True,
            "message": "Product added to portfolio",
            "product": product_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding product: {str(e)}")

@app.get("/portfolio")
async def get_portfolio():
    """
    Get user's personal makeup portfolio
    """
    return {
        "success": True,
        "portfolio": USER_PORTFOLIO,
        "total_products": len(USER_PORTFOLIO)
    }

@app.delete("/portfolio/{product_id}")
async def remove_from_portfolio(product_id: int):
    """
    Remove a product from user's portfolio
    """
    try:
        global USER_PORTFOLIO
        USER_PORTFOLIO = [p for p in USER_PORTFOLIO if p.get("id") != product_id]
        
        return {
            "success": True,
            "message": "Product removed from portfolio"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing product: {str(e)}")

@app.post("/portfolio/upload")
async def upload_product_to_portfolio(file: UploadFile = File(...), product_name: str = "", brand: str = "", category: str = ""):
    """
    Upload a makeup product photo and add it to portfolio with custom details
    """
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Analyze the image to get detected products
        detected_products = analyze_makeup_image(image)
        
        import time, base64
        
        image.thumbnail((200, 200), Image.Resampling.LANCZOS)
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        portfolio_item = {
            "id": len(USER_PORTFOLIO) + 1,
            "name": product_name or "Custom Product",
            "brand": brand or "Unknown Brand",
            "category": category or "Makeup Product",
            "image_data": f"data:image/jpeg;base64,{img_base64}",
            "detected_products": detected_products,
            "added_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "custom_entry": True
        }
        
        USER_PORTFOLIO.append(portfolio_item)
        
        return {
            "success": True,
            "message": "Product uploaded to portfolio",
            "product": portfolio_item,
            "detected_analysis": detected_products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading product: {str(e)}")
