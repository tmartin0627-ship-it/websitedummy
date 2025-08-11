import React, { useState, useRef } from 'react'
import './App.css'

interface MakeupProduct {
  name: string
  brand: string
  category: string
  description?: string
  ingredients: string[]
  confidence?: number
  source?: string
  manufacturer_url?: string
}

interface AnalysisResult {
  success: boolean
  products_detected: number
  products: MakeupProduct[]
}

function SimpleApp() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [apiKey, setApiKey] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string)
        setError(null)
      }
      reader.readAsDataURL(file)
    }
  }

  const analyzeImage = async () => {
    if (!selectedImage || !apiKey.trim()) {
      setError('Please provide both an image and API key')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      const formData = new FormData()
      
      const response = await fetch(selectedImage)
      const blob = await response.blob()
      formData.append('file', blob, 'image.jpg')
      formData.append('api_key', apiKey)

      const apiResponse = await fetch('http://localhost:8000/analyze-makeup', {
        method: 'POST',
        body: formData,
      })

      if (!apiResponse.ok) {
        throw new Error(`HTTP error! status: ${apiResponse.status}`)
      }

      const result = await apiResponse.json()
      setAnalysisResult(result)
    } catch (err) {
      setError(`Analysis failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const resetAnalysis = () => {
    setSelectedImage(null)
    setAnalysisResult(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(to bottom right, #fdf2f8, #faf5ff)', padding: '1rem' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
            Makeup Ingredient Analyzer
          </h1>
          <p style={{ fontSize: '1.125rem', color: '#6b7280' }}>
            Upload a photo of your makeup to discover the ingredients in each product
          </p>
        </div>

        <div style={{ display: 'grid', gap: '1.5rem', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
          {/* Upload Section */}
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              📷 Upload Your Photo
            </h3>
            <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
              Take or upload a clear photo of your makeup products
            </p>

            {/* API Key Input */}
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="api-key" style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '0.5rem' }}>
                OpenAI API Key
              </label>
              <input
                id="api-key"
                type="password"
                placeholder="Enter your OpenAI API key (sk-...)"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  outline: 'none'
                }}
              />
              <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                Your API key is used only for this analysis and is not stored.
              </p>
            </div>

            {/* Image Upload Area */}
            <div style={{ border: '2px dashed #d1d5db', borderRadius: '0.5rem', padding: '1.5rem', textAlign: 'center' }}>
              {selectedImage ? (
                <div>
                  <img
                    src={selectedImage}
                    alt="Selected makeup"
                    style={{ maxWidth: '100%', height: '200px', objectFit: 'contain', margin: '0 auto', borderRadius: '0.5rem', marginBottom: '1rem' }}
                  />
                  <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                    <button
                      onClick={analyzeImage}
                      disabled={isAnalyzing || !apiKey.trim()}
                      style={{
                        padding: '0.75rem 1.5rem',
                        backgroundColor: isAnalyzing || !apiKey.trim() ? '#9ca3af' : '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '0.375rem',
                        cursor: isAnalyzing || !apiKey.trim() ? 'not-allowed' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      {isAnalyzing ? '⏳ Analyzing...' : '👁️ Analyze Makeup'}
                    </button>
                    <button
                      onClick={resetAnalysis}
                      style={{
                        padding: '0.75rem 1.5rem',
                        backgroundColor: 'white',
                        color: '#374151',
                        border: '1px solid #d1d5db',
                        borderRadius: '0.375rem',
                        cursor: 'pointer'
                      }}
                    >
                      Choose Different Photo
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📤</div>
                  <div>
                    <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>
                      Click to upload or drag and drop
                    </p>
                    <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>
                      PNG, JPG, GIF up to 10MB
                    </p>
                  </div>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    style={{
                      marginTop: '1rem',
                      padding: '0.75rem 1.5rem',
                      backgroundColor: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '0.375rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      margin: '1rem auto 0'
                    }}
                  >
                    📤 Choose Photo
                  </button>
                </div>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              style={{ display: 'none' }}
            />

            {error && (
              <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '0.375rem', color: '#dc2626' }}>
                {error}
              </div>
            )}
          </div>

          {/* Results Section */}
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              📦 Analysis Results
            </h3>
            <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
              Detected makeup products and their ingredients
            </p>

            {!analysisResult && !isAnalyzing && (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.5 }}>📦</div>
                <p>Upload and analyze a photo to see results</p>
              </div>
            )}

            {isAnalyzing && (
              <div style={{ textAlign: 'center', padding: '2rem' }}>
                <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⏳</div>
                <p style={{ color: '#6b7280' }}>Analyzing your makeup...</p>
              </div>
            )}

            {analysisResult && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <h4 style={{ fontWeight: '600', fontSize: '1.125rem' }}>
                    Products Detected: {analysisResult.products_detected}
                  </h4>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {analysisResult.products.map((product, index) => (
                    <div key={index} style={{ border: '1px solid #e5e7eb', borderLeft: '4px solid #8b5cf6', borderRadius: '0.5rem', padding: '1rem' }}>
                      <div style={{ marginBottom: '0.75rem' }}>
                        <h5 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.25rem' }}>{product.name}</h5>
                        <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                          {product.brand} • {product.category}
                        </p>
                      </div>

                      {product.description && (
                        <p style={{ fontSize: '0.875rem', color: '#6b7280', fontStyle: 'italic', marginBottom: '0.75rem' }}>
                          {product.description}
                        </p>
                      )}

                      <div>
                        <h6 style={{ fontWeight: '500', marginBottom: '0.5rem', fontSize: '0.875rem', color: '#374151' }}>
                          Ingredients:
                        </h6>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginBottom: '0.5rem' }}>
                          {product.ingredients.map((ingredient, idx) => (
                            <span
                              key={idx}
                              style={{
                                fontSize: '0.75rem',
                                padding: '0.25rem 0.5rem',
                                backgroundColor: '#f3f4f6',
                                border: '1px solid #d1d5db',
                                borderRadius: '0.25rem'
                              }}
                            >
                              {ingredient}
                            </span>
                          ))}
                        </div>

                        {product.source && (
                          <div style={{ fontSize: '0.75rem', color: '#6b7280', borderTop: '1px solid #e5e7eb', paddingTop: '0.5rem' }}>
                            <p style={{ fontWeight: '500' }}>Ingredient Source:</p>
                            <p>{product.source}</p>
                            {product.manufacturer_url && (
                              <a
                                href={product.manufacturer_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ color: '#2563eb', textDecoration: 'underline' }}
                              >
                                Visit Manufacturer Website 🔗
                              </a>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.875rem', color: '#6b7280' }}>
          <p>
            This tool provides ingredient information based on image analysis.
            Always check product labels for complete and accurate ingredient lists.
          </p>
        </div>
      </div>
    </div>
  )
}

export default SimpleApp
