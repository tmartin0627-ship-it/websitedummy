import { useState, useRef, useEffect } from 'react'
import { Camera, Upload, Loader2, Eye, Package, FolderOpen, Plus, Trash2, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import './App.css'

interface MakeupProduct {
  name: string
  brand: string
  shade?: string
  ingredients: string[]
  category: string
  source?: string
  manufacturer_url?: string
  price_range?: string
  description?: string
}

interface AnalysisResult {
  success: boolean
  products_detected: number
  products: MakeupProduct[]
}

interface PortfolioItem {
  id: number
  name: string
  brand: string
  category: string
  image_data?: string
  detected_products?: MakeupProduct[]
  added_date: string
  custom_entry?: boolean
}

function App() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([])
  const [activeTab, setActiveTab] = useState<'analyze' | 'portfolio'>('analyze')
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false)
  const [portfolioUpload, setPortfolioUpload] = useState({
    name: '',
    brand: '',
    category: ''
  })
  const fileInputRef = useRef<HTMLInputElement>(null)
  const portfolioFileRef = useRef<HTMLInputElement>(null)

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string)
        setAnalysisResult(null)
        setError(null)
      }
      reader.readAsDataURL(file)
    }
  }

  const analyzeImage = async () => {
    if (!selectedImage || !fileInputRef.current?.files?.[0]) return

    setIsAnalyzing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', fileInputRef.current.files[0])

      const response = await fetch('https://app-prhccbfu.fly.dev/analyze-makeup', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to analyze image')
      }

      const result: AnalysisResult = await response.json()
      setAnalysisResult(result)
    } catch (err) {
      setError('Failed to analyze the image. Please try again.')
      console.error('Analysis error:', err)
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

  const loadPortfolio = async () => {
    setIsLoadingPortfolio(true)
    try {
      const response = await fetch('https://app-prhccbfu.fly.dev/portfolio')
      if (response.ok) {
        const data = await response.json()
        setPortfolio(data.portfolio || [])
      }
    } catch (err) {
      console.error('Failed to load portfolio:', err)
    } finally {
      setIsLoadingPortfolio(false)
    }
  }

  const addToPortfolio = async (product: MakeupProduct) => {
    try {
      const response = await fetch('https://app-prhccbfu.fly.dev/portfolio/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(product),
      })
      
      if (response.ok) {
        loadPortfolio()
      }
    } catch (err) {
      console.error('Failed to add to portfolio:', err)
    }
  }

  const uploadToPortfolio = async () => {
    if (!portfolioFileRef.current?.files?.[0] || !portfolioUpload.name) return

    try {
      const formData = new FormData()
      formData.append('file', portfolioFileRef.current.files[0])
      formData.append('product_name', portfolioUpload.name)
      formData.append('brand', portfolioUpload.brand)
      formData.append('category', portfolioUpload.category)

      const response = await fetch('https://app-prhccbfu.fly.dev/portfolio/upload', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        loadPortfolio()
        setPortfolioUpload({ name: '', brand: '', category: '' })
        if (portfolioFileRef.current) {
          portfolioFileRef.current.value = ''
        }
      }
    } catch (err) {
      console.error('Failed to upload to portfolio:', err)
    }
  }

  const removeFromPortfolio = async (productId: number) => {
    try {
      const response = await fetch(`https://app-prhccbfu.fly.dev/portfolio/${productId}`, {
        method: 'DELETE',
      })
      
      if (response.ok) {
        loadPortfolio()
      }
    } catch (err) {
      console.error('Failed to remove from portfolio:', err)
    }
  }

  useEffect(() => {
    if (activeTab === 'portfolio') {
      loadPortfolio()
    }
  }, [activeTab])

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Makeup Ingredient Analyzer
          </h1>
          <p className="text-lg text-gray-600">
            Upload a photo of your makeup to discover the ingredients in each product
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'analyze' | 'portfolio')} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="analyze" className="flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Analyze Makeup
            </TabsTrigger>
            <TabsTrigger value="portfolio" className="flex items-center gap-2">
              <FolderOpen className="w-4 h-4" />
              My Portfolio
            </TabsTrigger>
          </TabsList>

          <TabsContent value="analyze" className="mt-6">
            <div className="grid gap-6 md:grid-cols-2">
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="w-5 h-5" />
                Upload Your Photo
              </CardTitle>
              <CardDescription>
                Take or upload a clear photo of your makeup products
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                {selectedImage ? (
                  <div className="space-y-4">
                    <img
                      src={selectedImage}
                      alt="Selected makeup"
                      className="max-w-full h-48 object-contain mx-auto rounded-lg"
                    />
                    <div className="flex gap-2 justify-center">
                      <Button onClick={analyzeImage} disabled={isAnalyzing}>
                        {isAnalyzing ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <Eye className="w-4 h-4 mr-2" />
                            Analyze Makeup
                          </>
                        )}
                      </Button>
                      <Button variant="outline" onClick={resetAnalysis}>
                        Choose Different Photo
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                    <div>
                      <p className="text-gray-600 mb-2">
                        Click to upload or drag and drop
                      </p>
                      <p className="text-sm text-gray-500">
                        PNG, JPG, GIF up to 10MB
                      </p>
                    </div>
                    <Button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Choose Photo
                    </Button>
                  </div>
                )}
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="w-5 h-5" />
                Analysis Results
              </CardTitle>
              <CardDescription>
                Detected makeup products and their ingredients
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!analysisResult && !isAnalyzing && (
                <div className="text-center py-8 text-gray-500">
                  <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Upload and analyze a photo to see results</p>
                </div>
              )}

              {isAnalyzing && (
                <div className="text-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-purple-600" />
                  <p className="text-gray-600">Analyzing your makeup...</p>
                </div>
              )}

              {analysisResult && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-lg">
                      Products Detected: {analysisResult.products_detected}
                    </h3>
                  </div>

                  <div className="space-y-4">
                    {analysisResult.products.map((product, index) => (
                      <Card key={index} className="border-l-4 border-l-purple-500">
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <CardTitle className="text-lg">{product.name}</CardTitle>
                              <CardDescription className="text-sm">
                                {product.brand} {product.shade && `• ${product.shade}`} • {product.category}
                              </CardDescription>
                              {product.price_range && (
                                <p className="text-xs text-green-600 font-medium mt-1">
                                  {product.price_range}
                                </p>
                              )}
                            </div>
                            <div className="flex flex-col gap-2">
                              <Badge variant="secondary">{product.category}</Badge>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => addToPortfolio(product)}
                                className="text-xs"
                              >
                                <Plus className="w-3 h-3 mr-1" />
                                Add to Portfolio
                              </Button>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          {product.description && (
                            <p className="text-sm text-gray-600 italic">
                              {product.description}
                            </p>
                          )}
                          
                          <div>
                            <h4 className="font-medium mb-2 text-sm text-gray-700">
                              Ingredients:
                            </h4>
                            <div className="flex flex-wrap gap-1 mb-2">
                              {product.ingredients.map((ingredient, idx) => (
                                <Badge
                                  key={idx}
                                  variant="outline"
                                  className="text-xs"
                                >
                                  {ingredient}
                                </Badge>
                              ))}
                            </div>
                            
                            {product.source && (
                              <div className="text-xs text-gray-500 border-t pt-2">
                                <p className="font-medium">Ingredient Source:</p>
                                <p>{product.source}</p>
                                {product.manufacturer_url && (
                                  <a
                                    href={product.manufacturer_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:underline inline-flex items-center gap-1"
                                  >
                                    Visit Manufacturer Website
                                    <ExternalLink className="w-3 h-3" />
                                  </a>
                                )}
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
            </div>
          </TabsContent>

          <TabsContent value="portfolio" className="mt-6">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Plus className="w-5 h-5" />
                    Add New Product
                  </CardTitle>
                  <CardDescription>
                    Upload a photo and details of your makeup product
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="text-sm font-medium">Product Name</label>
                      <Input
                        placeholder="e.g., Rouge Dior Lipstick"
                        value={portfolioUpload.name}
                        onChange={(e) => setPortfolioUpload(prev => ({ ...prev, name: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Brand</label>
                      <Input
                        placeholder="e.g., Dior"
                        value={portfolioUpload.brand}
                        onChange={(e) => setPortfolioUpload(prev => ({ ...prev, brand: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Category</label>
                      <Input
                        placeholder="e.g., Lip Color"
                        value={portfolioUpload.category}
                        onChange={(e) => setPortfolioUpload(prev => ({ ...prev, category: e.target.value }))}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Product Photo</label>
                    <div className="mt-1">
                      <input
                        ref={portfolioFileRef}
                        type="file"
                        accept="image/*"
                        className="hidden"
                      />
                      <Button
                        variant="outline"
                        onClick={() => portfolioFileRef.current?.click()}
                        className="w-full"
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        Choose Photo
                      </Button>
                    </div>
                  </div>

                  <Button
                    onClick={uploadToPortfolio}
                    disabled={!portfolioUpload.name || !portfolioFileRef.current?.files?.[0]}
                    className="w-full"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add to Portfolio
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Package className="w-5 h-5" />
                      My Products ({portfolio.length})
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isLoadingPortfolio ? (
                    <div className="text-center py-8">
                      <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-purple-600" />
                      <p className="text-gray-600">Loading portfolio...</p>
                    </div>
                  ) : portfolio.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No products in your portfolio yet</p>
                      <p className="text-sm">Add products by analyzing photos or uploading manually</p>
                    </div>
                  ) : (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {portfolio.map((item) => (
                        <Card key={item.id} className="relative">
                          <CardHeader className="pb-3">
                            <div className="flex items-start justify-between">
                              <div>
                                <CardTitle className="text-base">{item.name}</CardTitle>
                                <CardDescription className="text-sm">
                                  {item.brand} • {item.category}
                                </CardDescription>
                                <p className="text-xs text-gray-500 mt-1">
                                  Added {new Date(item.added_date).toLocaleDateString()}
                                </p>
                              </div>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => removeFromPortfolio(item.id)}
                                className="text-red-500 hover:text-red-700"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </CardHeader>
                          <CardContent>
                            {item.image_data && (
                              <img
                                src={item.image_data}
                                alt={item.name}
                                className="w-full h-32 object-cover rounded-lg mb-3"
                              />
                            )}
                            {item.detected_products && item.detected_products.length > 0 && (
                              <div>
                                <p className="text-xs font-medium text-gray-700 mb-1">
                                  Detected Analysis:
                                </p>
                                <div className="flex flex-wrap gap-1">
                                  {item.detected_products.slice(0, 3).map((product, idx) => (
                                    <Badge key={idx} variant="outline" className="text-xs">
                                      {product.category}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            This tool provides ingredient information based on image analysis.
            Always check product labels for complete and accurate ingredient lists.
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
