import { useEffect, useState } from 'react'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function App() {
  const [apiStatus, setApiStatus] = useState('Checking API...')

  useEffect(() => {
    fetch(`${apiBaseUrl}/health`)
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then(() => setApiStatus('API connected'))
      .catch(() => setApiStatus('API unavailable'))
  }, [])

  return (
    <main>
      <h1>Arabic Apparel & Stickers</h1>
      <p>Full-stack foundation is ready for the first feature.</p>
      <p aria-live="polite">{apiStatus}</p>
    </main>
  )
}

export default App
