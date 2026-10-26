import { useEffect, useMemo, useState } from 'react'
import { MAX_PERSONALIZATION_GRAPHEMES, normalizeAndValidateArabicLetter, normalizeAndValidateArabicText } from './personalization'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const fonts = ['Amiri', 'Cairo', 'Tajawal']
const stickerColours = [
  ['Black', '#000000'], ['White', '#FFFFFF'], ['Yellow', '#FFEA00'], ['Light Blue', '#37C5D3'], ['Red', '#E52B24'],
  ['Grass Green', '#3AAF2A'], ['Pink', '#EB78B8'], ['Royal Blue', '#2F4A92'], ['Purple', '#5A3AA5'], ['Brown', '#4B2117'],
  ['Lake Blue', '#167D98'], ['Rose Gold', '#B9999F'], ['Dark Yellow', '#F18A00'], ['Rose Red', '#BF1831'], ['Aqua Blue', '#258FC6'],
  ['Dark Green', '#123D2D'], ['Green', '#078652'], ['Gold', '#D8BA39'], ['Silver', '#C8CDD0'], ['Orange', '#FF6413'],
]
const textProducts = new Set(['personalized-arabic-rectangular-tag', 'small-arabic-letter-tag', 'personalized-arabic-htv-sticker', 'be-seen-boys-sweater', 'be-seen-mens-sweater'])

type ProductPrice = { option_key: string; option_value: string; price_pence: number; pair_price_pence: number | null }
type Product = { id: number; slug: string; name: string; description: string; category: string; prices: ProductPrice[] }
type Customization = { text: string; font: string; size: string; colour: string; quantity: number }
type Quote = { price_pence: number; quantity: number; pair_price_pence: number | null }

function formatPrice(pence: number): string { return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(pence / 100) }
function initialCustomization(): Customization { return { text: '', font: 'Amiri', size: '5x5', colour: '#000000', quantity: 1 } }

function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [customization, setCustomization] = useState<Customization | null>(null)
  const [quote, setQuote] = useState<Quote | null>(null)
  const [quoteError, setQuoteError] = useState('')
  const [error, setError] = useState('')
  const [customerName, setCustomerName] = useState('')
  const [customerContact, setCustomerContact] = useState('')
  const [orderMessage, setOrderMessage] = useState('')

  useEffect(() => {
    fetch(`${apiBaseUrl}/api/products`).then((response) => response.ok ? response.json() : Promise.reject())
      .then((data: Product[]) => setProducts(data)).catch(() => setError('The catalogue is unavailable. Please try again shortly.'))
  }, [])

  const requiresText = Boolean(selectedProduct && textProducts.has(selectedProduct.slug))
  const isLetterTag = selectedProduct?.slug === 'small-arabic-letter-tag'
  const textValidation = useMemo(
    () => isLetterTag ? normalizeAndValidateArabicLetter(customization?.text ?? '') : normalizeAndValidateArabicText(customization?.text ?? ''),
    [customization?.text, isLetterTag],
  )

  useEffect(() => {
    if (!selectedProduct || !customization || (requiresText && textValidation.error)) return
    const options: Record<string, string> = {}
    if (selectedProduct.slug === 'small-be-seen-tag') options.design = 'be-seen'
    if (requiresText) Object.assign(options, { text: textValidation.value, font: customization.font })
    if (selectedProduct.slug === 'personalized-arabic-htv-sticker') Object.assign(options, { size: customization.size, colour: customization.colour })
    let cancelled = false
    fetch(`${apiBaseUrl}/api/products/${selectedProduct.id}/price`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ options, quantity: customization.quantity }) })
      .then(async (response) => { const data = await response.json(); if (!response.ok) throw new Error(data.detail ?? 'Unable to calculate price.'); return data as Quote })
      .then((data) => { if (!cancelled) { setQuote(data); setQuoteError('') } })
      .catch((requestError: Error) => { if (!cancelled) { setQuote(null); setQuoteError(requestError.message) } })
    return () => { cancelled = true }
  }, [customization, requiresText, selectedProduct, textValidation.error, textValidation.value])

  function update(change: Partial<Customization>) { setCustomization((current) => current ? { ...current, ...change } : current) }
  function openCustomizer(product: Product) { setSelectedProduct(product); setCustomization(initialCustomization()); setQuote(null); setQuoteError(''); setOrderMessage('') }
  function orderOptions(): Record<string, string> {
    const options: Record<string, string> = {}
    if (!selectedProduct || !customization) return options
    if (selectedProduct.slug === 'small-be-seen-tag') options.design = 'be-seen'
    if (requiresText) Object.assign(options, { text: textValidation.value, font: customization.font })
    if (selectedProduct.slug === 'personalized-arabic-htv-sticker') Object.assign(options, { size: customization.size, colour: customization.colour })
    return options
  }
  async function submitOrder(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedProduct || !customization || !quote) return
    setOrderMessage('Sending order...')
    try {
      const response = await fetch(`${apiBaseUrl}/api/orders`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ product_id: selectedProduct.id, options: orderOptions(), quantity: customization.quantity, customer_name: customerName, customer_contact: customerContact }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? 'Unable to send your order.')
      setOrderMessage(`Order request #${data.id} sent. We will contact you shortly.`)
    } catch (requestError) { setOrderMessage(requestError instanceof Error ? requestError.message : 'Unable to send your order.') }
  }
  const previewText = selectedProduct?.slug === 'small-be-seen-tag' ? 'Be \u0633' : textValidation.value || '\u0627\u0643\u062a\u0628 \u0627\u0633\u0645\u0643'
  const previewStyle = { fontFamily: `${customization?.font ?? 'Amiri'}, "Noto Naskh Arabic", serif`, color: selectedProduct?.slug === 'personalized-arabic-htv-sticker' ? customization?.colour : undefined }

  return <main className="catalogue-shell">
    <header className="masthead"><p className="eyebrow">CUSTOM TEXTILE STUDIO</p><h1>Arabic Apparel & Stickers</h1><p>Arabic-first lettering for apparel, transfers, and Be Seen tags.</p></header>
    {error && <p role="alert">{error}</p>}
    {!error && products.length === 0 && <p>Loading catalogue...</p>}
    <section className="catalogue-grid" aria-label="Product catalogue">{products.map((product) => <article className="product-card" key={product.id}>
      <p className="product-category">{product.category}</p><h2>{product.name}</h2><p>{product.description}</p>
      <p className="demo-price">Demo price from {formatPrice(Math.min(...product.prices.map((price) => price.price_pence)))}</p>
      <button type="button" onClick={() => openCustomizer(product)}>{textProducts.has(product.slug) ? 'Customize' : 'View details'}</button>
    </article>)}</section>
    {selectedProduct && customization && <section className="customizer" aria-labelledby="customizer-title">
      <div className="customizer-heading"><div><p className="product-category">{selectedProduct.category}</p><h2 id="customizer-title">{selectedProduct.name}</h2></div><button type="button" className="close-button" onClick={() => setSelectedProduct(null)}>Close</button></div>
      <div className="customizer-layout"><form className="customizer-form" onSubmit={(event) => event.preventDefault()}>
        {selectedProduct.slug === 'small-be-seen-tag' && <p>Fixed Be Seen design: <b>Be <span dir="rtl" lang="ar">\u0633</span></b></p>}
        {requiresText && <label htmlFor="personalized-text">{isLetterTag ? 'Arabic letter' : 'Arabic text or name'}
          <textarea id="personalized-text" value={customization.text} onChange={(event) => update({ text: event.target.value.normalize('NFC') })} aria-describedby="text-rules text-error" dir="rtl" lang="ar" rows={isLetterTag ? 1 : 3} />
          <small id="text-rules">{isLetterTag ? 'One Arabic letter, with optional diacritics.' : `Arabic letters, diacritics, spaces, hyphens, and Arabic or Western digits. Maximum ${MAX_PERSONALIZATION_GRAPHEMES} graphemes.`}</small>
          {textValidation.error && <span id="text-error" className="field-error" role="alert">{textValidation.error}</span>}
        </label>}
        {requiresText && <label>Font<select value={customization.font} onChange={(event) => update({ font: event.target.value })}>{fonts.map((font) => <option key={font}>{font}</option>)}</select></label>}
        {selectedProduct.slug === 'personalized-arabic-htv-sticker' && <><label>Sticker size<select value={customization.size} onChange={(event) => update({ size: event.target.value })}>{[['5x5', '5 x 5 inches'], ['9x4', '9 x 4 inches'], ['12x3', '12 x 3 inches']].map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <fieldset><legend>HTV colour</legend><div className="colour-choices">{stickerColours.map(([name, colour]) => <label className="colour-choice" key={colour}><input type="radio" name="colour" value={colour} checked={customization.colour === colour} onChange={() => update({ colour })} /><span style={{ backgroundColor: colour }} aria-hidden="true" /><span>{name}</span></label>)}</div></fieldset></>}
        <label>Quantity<input type="number" min="1" value={customization.quantity} onChange={(event) => update({ quantity: Math.max(1, Number(event.target.value) || 1) })} /></label>
      </form>
      <aside className={`preview preview-${selectedProduct.slug}`} aria-label="Illustrative live preview"><p className="preview-label">Illustrative preview - not production-accurate</p><div className="preview-surface"><span className="preview-text" dir="rtl" lang="ar" style={previewStyle}>{previewText}</span></div><div className="quote" aria-live="polite">{quote && <strong>Demo total for {quote.quantity}: {formatPrice(quote.price_pence)}</strong>}{!quote && !quoteError && <span>{requiresText ? 'Enter valid personalization to calculate a demo price.' : 'Calculating demo price...'}</span>}{quoteError && <span role="alert">{quoteError}</span>}</div>
        {quote && <form className="order-form" onSubmit={submitOrder}><h3>Send order request</h3><label>Your name<input required value={customerName} onChange={(event) => setCustomerName(event.target.value)} /></label><label>Email or phone<input required value={customerContact} onChange={(event) => setCustomerContact(event.target.value)} /></label><button type="submit">Send order request</button>{orderMessage && <p aria-live="polite">{orderMessage}</p>}</form>}
      </aside>
      </div></section>}
  </main>
}

export default App
