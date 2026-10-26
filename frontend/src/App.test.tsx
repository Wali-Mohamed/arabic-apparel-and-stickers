import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App'

const products = [
  { id: 1, slug: 'small-be-seen-tag', name: 'Small Be Seen tag', description: 'Fixed tag.', category: 'Tags', prices: [{ option_key: 'standard', option_value: 'standard', price_pence: 500, pair_price_pence: null }] },
  { id: 2, slug: 'small-arabic-letter-tag', name: 'Small Arabic letter-only tag', description: 'Letter tag.', category: 'Tags', prices: [{ option_key: 'standard', option_value: 'standard', price_pence: 500, pair_price_pence: 850 }] },
  { id: 3, slug: 'personalized-arabic-htv-sticker', name: 'Personalized Arabic HTV sticker', description: 'Sticker.', category: 'HTV', prices: [{ option_key: 'size', option_value: '5x5', price_pence: 500, pair_price_pence: null }] },
  { id: 4, slug: 'big-be-seen-tag', name: 'Big Be Seen tag', description: 'Large fixed tag.', category: 'Tags', prices: [{ option_key: 'standard', option_value: 'standard', price_pence: 1000, pair_price_pence: null }] },
]

afterEach(() => vi.unstubAllGlobals())

function mockApi() {
  vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
    if (url.endsWith('/api/products')) return Promise.resolve({ ok: true, json: async () => products })
    const body = JSON.parse(String(init?.body))
    return Promise.resolve({ ok: true, json: async () => ({ price_pence: body.quantity === 2 ? 850 : 500, quantity: body.quantity, pair_price_pence: 850 }) })
  }))
}

describe('App', () => {
  it('shows the fixed B-Series Be Seen tag and quotes its price', async () => {
    mockApi(); render(<App />)
    const card = (await screen.findByRole('heading', { name: 'Small Be Seen tag' })).closest('article')!
    fireEvent.click(within(card).getByRole('button', { name: 'View details' }))
    expect(within(screen.getByRole('region', { name: 'Small Be Seen tag' })).getByText(/Fixed Be Seen design/)).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText('Demo total for 1: £5.00')).toBeInTheDocument())
  })

  it('validates letter-only input and posts a quantity quote', async () => {
    mockApi(); render(<App />)
    fireEvent.click((await screen.findAllByRole('button', { name: 'Customize' }))[0])
    const text = screen.getByRole('textbox')
    fireEvent.change(text, { target: { value: 'ab' } })
    expect(screen.getByRole('alert')).toHaveTextContent('Use Arabic letters')
    fireEvent.change(text, { target: { value: '\u0628' } })
    fireEvent.change(screen.getByRole('spinbutton'), { target: { value: '2' } })
    await waitFor(() => expect(screen.getByText('Demo total for 2: £8.50')).toBeInTheDocument())
  })

  it('submits the fixed tag with the same supported design as its quote', async () => {
    const api = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/api/products')) return Promise.resolve({ ok: true, json: async () => products })
      if (url.endsWith('/api/orders')) return Promise.resolve({ ok: true, json: async () => ({ id: 42 }) })
      return Promise.resolve({ ok: true, json: async () => ({ price_pence: 500, quantity: 1 }) })
    })
    vi.stubGlobal('fetch', api)
    render(<App />)
    const card = (await screen.findByRole('heading', { name: 'Small Be Seen tag' })).closest('article')!
    fireEvent.click(within(card).getByRole('button', { name: 'View details' }))
    fireEvent.change(await screen.findByLabelText('Your name'), { target: { value: 'Synthetic customer' } })
    fireEvent.change(screen.getByLabelText('Email or phone'), { target: { value: 'test@example.invalid' } })
    fireEvent.click(screen.getByRole('button', { name: 'Send order request' }))
    await screen.findByText(/Order request #42 sent/)
    const request = api.mock.calls.find(([url]) => url.endsWith('/api/orders'))
    expect(JSON.parse(String(request?.[1]?.body)).options).toEqual({ design: 'be-seen' })
  })

  it.each([
    ['Small Be Seen tag', 1, { design: 'be-seen' }],
    ['Big Be Seen tag', 4, {}],
  ] as const)('keeps Be left of Arabic seen throughout %s ordering', async (name, id, options) => {
    const api = vi.fn((url: string) => Promise.resolve({
      ok: true,
      json: async () => url.endsWith('/api/products') ? products
        : url.endsWith('/api/orders') ? { id: 42 }
        : { price_pence: id === 1 ? 500 : 1000, quantity: 1 },
    }))
    vi.stubGlobal('fetch', api)
    // Exercise the component under an RTL ancestor, not just an English page.
    render(<div dir="rtl"><App /></div>)
    function expectDesign(scope: HTMLElement) {
      const design = within(scope).getByLabelText('Be \u0633')
      expect(design).toHaveAttribute('dir', 'ltr')
      expect(design).toHaveStyle({ display: 'inline-flex', flexDirection: 'row', direction: 'ltr', unicodeBidi: 'isolate' })
      const [english, arabic] = Array.from(design.children)
      expect(english).toHaveTextContent(/^Be$/)
      expect(english).toHaveAttribute('dir', 'ltr')
      expect(english).toHaveAttribute('lang', 'en')
      expect(arabic).toHaveTextContent(/^\u0633$/)
      expect(arabic).toHaveAttribute('dir', 'rtl')
      expect(arabic).toHaveAttribute('lang', 'ar')
      expect(english).toHaveStyle({ unicodeBidi: 'isolate' })
      expect(arabic).toHaveStyle({ unicodeBidi: 'isolate' })
    }
    const card = (await screen.findByRole('heading', { name })).closest('article')!
    expectDesign(card)
    fireEvent.click(within(card).getByRole('button', { name: 'View details' }))
    const customizer = screen.getByRole('region', { name })
    expect(within(customizer).queryByRole('textbox', { name: /Arabic/ })).not.toBeInTheDocument()
    expect(within(customizer).queryByRole('combobox')).not.toBeInTheDocument()
    expectDesign(screen.getByLabelText('Illustrative live preview').querySelector('.preview-surface')!)
    expectDesign(await screen.findByLabelText('Order summary'))
    fireEvent.change(screen.getByLabelText('Your name'), { target: { value: 'Synthetic customer' } })
    fireEvent.change(screen.getByLabelText('Email or phone'), { target: { value: 'test@example.invalid' } })
    fireEvent.click(screen.getByRole('button', { name: 'Send order request' }))
    expectDesign(await screen.findByText(/Order request #42 sent/))
    const calls = api.mock.calls as unknown as [string, RequestInit?][]
    const order = calls.find(([url]) => url.endsWith('/api/orders'))
    const quote = calls.find(([url]) => url.endsWith(`/api/products/${id}/price`))
    expect(JSON.parse(String(order?.[1]?.body))).toMatchObject({ product_id: id, options })
    expect(JSON.parse(String(quote?.[1]?.body)).options).toEqual(options)
  })
})
