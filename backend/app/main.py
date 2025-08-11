from fastapi import FastAPI, File, UploadFile, HTTPException, Form
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


USER_PORTFOLIO = []

def analyze_makeup_image(image: Image.Image, api_key: str = None) -> List[Dict[str, Any]]:
    """
    Analyze the image to detect makeup products using OpenAI Vision API.
    Returns raw GPT-4 analysis with AI-identified ingredients.
    """
    try:
        current_api_key = api_key or openai.api_key
        
        if not current_api_key:
            return [{
                "name": "Unknown Makeup Product",
                "brand": "Unknown",
                "type": "makeup",
                "confidence": 0.5,
                "description": "API key not available for detailed analysis",
                "ingredients": ["Unable to analyze ingredients without API key"],
                "source": "Fallback response"
            }]
        
        img_buffer = io.BytesIO()
        image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        image.save(img_buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        prompt = """Analyze this image and identify any makeup products visible. For each product you detect, provide detailed information including likely ingredients.

        Look specifically for:
        - Lipstick (red, pink, or colored lip products)
        - Foundation (liquid makeup, skin-tone products in bottles/tubes)
        - Mascara (dark eye makeup in tubes)
        - Eyeshadow (colored powders in palettes or compacts)
        - Blush, bronzer, concealer, or other makeup items

        Do NOT identify:
        - Skincare products (moisturizers, serums, cleansers)
        - General beauty tools
        - Non-makeup items

        For each detected makeup product, respond with a JSON array containing objects with:
        - "name": estimated product name or generic name
        - "brand": estimated brand if visible, or "Unknown"
        - "type": product category (lipstick, foundation, mascara, eyeshadow, etc.)
        - "confidence": number from 0-1 indicating detection confidence
        - "description": detailed description of what you see
        - "ingredients": array of likely ingredients based on the product type (use common cosmetic ingredients)
        - "source": "AI Analysis based on product type and visual characteristics"

        For ingredients, include typical cosmetic ingredients for that product type. For example:
        - Lipstick: waxes, oils, pigments, preservatives
        - Foundation: water, silicones, pigments, emulsifiers
        - Mascara: water, waxes, pigments, film formers
        - Eyeshadow: talc, mica, pigments, binders

        If no makeup products are clearly visible, return an empty array []."""
        
        client = openai.OpenAI(api_key=current_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
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
            max_tokens=1000,
            temperature=0.1
        )
        
        response_text = response.choices[0].message.content
        
        try:
            detected_items = json.loads(response_text)
            
            filtered_products = []
            for item in detected_items:
                if item.get("confidence", 0) > 0.3:  # Lower threshold for more results
                    filtered_products.append(item)
            
            return filtered_products if filtered_products else []
        
        except json.JSONDecodeError:
            return [{
                "name": "Detected Makeup Product",
                "brand": "Unknown",
                "type": "makeup",
                "confidence": 0.7,
                "description": response_text,
                "ingredients": ["Analysis available in description"],
                "source": "AI Text Analysis"
            }]
        
    except Exception as api_error:
        print(f"OpenAI Vision API failed: {api_error}")
        return [{
            "name": "Analysis Error",
            "brand": "Unknown",
            "type": "error",
            "confidence": 0.0,
            "description": f"Error analyzing image: {str(api_error)}",
            "ingredients": ["Unable to analyze due to error"],
            "source": "Error response"
        }]

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/analyze-makeup")
async def analyze_makeup(file: UploadFile = File(...), api_key: str = Form(None)):
    """
    Analyze uploaded makeup photo and return detected products with ingredients
    """
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        detected_products = analyze_makeup_image(image, api_key)
        
        if not detected_products:
            detected_products = [
                {
                    "name": "No Makeup Products Detected",
                    "brand": "N/A",
                    "type": "none",
                    "confidence": 0.0,
                    "description": "No clear makeup products were identified in this image. Try uploading an image with visible makeup products like lipstick, foundation, mascara, or eyeshadow.",
                    "ingredients": ["No products detected"],
                    "source": "AI Analysis"
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
    Get sample makeup product types for reference
    """
    sample_products = [
        {
            "name": "Sample Lipstick",
            "type": "lipstick",
            "description": "AI will analyze and identify actual products from uploaded images"
        },
        {
            "name": "Sample Foundation", 
            "type": "foundation",
            "description": "AI will analyze and identify actual products from uploaded images"
        },
        {
            "name": "Sample Mascara",
            "type": "mascara", 
            "description": "AI will analyze and identify actual products from uploaded images"
        },
        {
            "name": "Sample Eyeshadow",
            "type": "eyeshadow",
            "description": "AI will analyze and identify actual products from uploaded images"
        }
    ]
    
    return {
        "success": True,
        "products": sample_products,
        "note": "These are sample product types. Upload images for AI analysis of actual products."
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
