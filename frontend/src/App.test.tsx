import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App'

const product = {
  id: 1,
  slug: 'high-visibility-tags',
  name: 'High-Visibility Tags',
  description: 'Arabic identification tags.',
  category: 'High-Visibility Tags',
  configuration_options: {
    fixed_designs: [{ name: 'B-Series', arabic_text: 'ب س' }],
  },
  prices: [{ option_key: 'design', option_value: 'b-series', price_pence: 599 }],
}

afterEach(() => vi.unstubAllGlobals())

describe('App', () => {
  it('renders products returned by the API and shows their detail view', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [product] }))
    render(<App />)

    expect(await screen.findByRole('heading', { name: 'High-Visibility Tags' })).toBeInTheDocument()
    expect(screen.getByText('Demo price from £5.99')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'View configuration' }))

    expect(screen.getByText(/ب س/)).toBeInTheDocument()
    expect(screen.getByText('Demonstration prices')).toBeInTheDocument()
  })

  it('shows an error when the catalogue request fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }))
    render(<App />)

    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('catalogue is unavailable'))
  })
})
