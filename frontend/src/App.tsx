import { useEffect, useState } from 'react'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type Product = {
  id: number
  slug: string
  name: string
  description: string
  category: string
  configuration_options: Record<string, unknown>
  prices: ProductPrice[]
}

type ProductPrice = {
  option_key: string
  option_value: string
  price_pence: number
}

function formatOption(value: unknown): string {
  if (Array.isArray(value)) {
    return value
      .map((item) => (typeof item === 'object' ? JSON.stringify(item) : String(item)))
      .join(', ')
  }
  return typeof value === 'object' ? JSON.stringify(value) : String(value)
}

function formatPrice(pricePence: number): string {
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(pricePence / 100)
}

function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${apiBaseUrl}/api/products`)
      .then((response) => (response.ok ? response.json() : Promise.reject(response)))
      .then((data: Product[]) => setProducts(data))
      .catch(() => setError('The catalogue is unavailable. Please try again shortly.'))
  }, [])

  return (
    <main className="catalogue-shell">
      <header className="masthead">
        <p className="eyebrow">CUSTOM TEXTILE STUDIO</p>
        <h1>Arabic Apparel & Stickers</h1>
        <p>Designed for clear Arabic type, bold colour, and high-visibility workwear.</p>
      </header>

      {error && <p role="alert">{error}</p>}
      {!error && products.length === 0 && <p>Loading catalogue...</p>}

      <section className="catalogue-grid" aria-label="Product catalogue">
        {products.map((product) => (
          <article className="product-card" key={product.id}>
            <p className="product-category">{product.category}</p>
            <h2>{product.name}</h2>
            <p>{product.description}</p>
            <p className="demo-price">Demo price from {formatPrice(Math.min(...product.prices.map((price) => price.price_pence)))}</p>
            <button type="button" onClick={() => setSelectedProduct(product)}>
              View configuration
            </button>
          </article>
        ))}
      </section>

      {selectedProduct && (
        <section className="product-detail" aria-live="polite">
          <div>
            <p className="product-category">{selectedProduct.category}</p>
            <h2>{selectedProduct.name}</h2>
            <p>{selectedProduct.description}</p>
          </div>
          <button type="button" className="close-button" onClick={() => setSelectedProduct(null)}>
            Close
          </button>
          <dl>
            {Object.entries(selectedProduct.configuration_options).map(([name, value]) => (
              <div key={name}>
                <dt>{name.replace(/_/g, ' ')}</dt>
                <dd dir={name === 'fixed_designs' ? 'rtl' : undefined}>{formatOption(value)}</dd>
              </div>
            ))}
          </dl>
          <div className="price-list">
            <h3>Demonstration prices</h3>
            {selectedProduct.prices.map((price) => (
              <p key={`${price.option_key}-${price.option_value}`}>
                {price.option_key.replace(/_/g, ' ')}: {price.option_value} - {formatPrice(price.price_pence)}
              </p>
            ))}
          </div>
        </section>
      )}
    </main>
  )
}

export default App
