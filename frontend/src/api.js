const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json()
}

export async function fetchCars({
  page = 1, limit = 20, make, model, year_from, year_to,
  price_min, price_max, fuel, transmission, body_type, color,
  steering, drive_type, condition, doors, leasing, location,
} = {}) {
  const params = new URLSearchParams()
  params.set('page', page)
  params.set('limit', limit)
  if (make) params.set('make', make)
  if (model) params.set('model', model)
  if (year_from) params.set('year_from', year_from)
  if (year_to) params.set('year_to', year_to)
  if (price_min) params.set('price_min', price_min)
  if (price_max) params.set('price_max', price_max)
  if (fuel) params.set('fuel', fuel)
  if (transmission) params.set('transmission', transmission)
  if (body_type) params.set('body_type', body_type)
  if (color) params.set('color', color)
  if (steering) params.set('steering', steering)
  if (drive_type) params.set('drive_type', drive_type)
  if (condition) params.set('condition', condition)
  if (doors) params.set('doors', doors)
  if (leasing) params.set('leasing', leasing)
  if (location) params.set('location', location)
  return request(`/cars?${params.toString()}`)
}

export async function fetchCar(id) {
  return request(`/cars/${id}`)
}

export async function fetchSimilarCars(id) {
  return request(`/cars/${id}/similar`)
}

export async function triggerScrape() {
  return request('/scrape', { method: 'POST' })
}

export async function fetchStats() {
  return request('/stats')
}
