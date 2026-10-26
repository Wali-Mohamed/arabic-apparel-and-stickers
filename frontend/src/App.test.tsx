import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App'

const products = [
  { id: 1, slug: 'small-be-seen-tag', name: 'Small Be Seen tag', description: 'Fixed tag.', category: 'Tags', prices: [{ option_key: 'standard', option_value: 'standard', price_pence: 500, pair_price_pence: null }] },
  { id: 2, slug: 'small-arabic-letter-tag', name: 'Small Arabic letter-only tag', description: 'Letter tag.', category: 'Tags', prices: [{ option_key: 'standard', option_value: 'standard', price_pence: 500, pair_price_pence: 850 }] },
  { id: 3, slug: 'personalized-arabic-htv-sticker', name: 'Personalized Arabic HTV sticker', description: 'Sticker.', category: 'HTV', prices: [{ option_key: 'size', option_value: '5x5', price_pence: 500, pair_price_pence: null }] },
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
    fireEvent.click(await screen.findByRole('button', { name: 'View details' }))
    expect(screen.getByText(/Fixed Be Seen design/)).toBeInTheDocument()
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
    fireEvent.click(await screen.findByRole('button', { name: 'View details' }))
    fireEvent.change(await screen.findByLabelText('Your name'), { target: { value: 'Synthetic customer' } })
    fireEvent.change(screen.getByLabelText('Email or phone'), { target: { value: 'test@example.invalid' } })
    fireEvent.click(screen.getByRole('button', { name: 'Send order request' }))
    await screen.findByText(/Order request #42 sent/)
    const request = api.mock.calls.find(([url]) => url.endsWith('/api/orders'))
    expect(JSON.parse(String(request?.[1]?.body)).options).toEqual({ design: 'be-seen' })
  })
})
