import { useState } from 'react'
import { SlidersHorizontal } from 'lucide-react'

const MAKES = [
  '', 'Toyota', 'Honda', 'Hyundai', 'Kia', 'Nissan', 'Mazda',
  'Suzuki', 'Mitsubishi', 'BMW', 'Mercedes-Benz', 'Audi',
  'Volkswagen', 'Ford', 'Chevrolet', 'Lexus', 'Subaru',
  'Haval', 'Changan', 'Geely', 'BYD', 'Tesla',
  'Infiniti', 'Acura', 'Jeep', 'Lada', 'UAZ', 'Land Rover',
]

const FUEL_TYPES = ['', 'Бензин', 'Дизель', 'Хайбрид', 'Цахилгаан', 'Газ']

const TRANSMISSIONS = ['', 'Автомат', 'Механик']

const BODY_TYPES = ['', 'Суудлын тэрэг', 'Жийп', 'Гэр бүлийн']

const COLORS = [
  '', 'Цагаан', 'Хар', 'Цэнхэр', 'Хөх', 'Саарал', 'Улаан',
  'Ногоон', 'Шар', 'Хүрэн', 'Боронзон', 'Хар саарал', 'Бусад',
]

const STEERING = ['', 'Зүүн', 'Буруу']

const DRIVE_TYPES = ['', 'Урдаа FWD', 'Арын RWD', '4WD']

const CONDITIONS = [
  '', 'Дугаартай нь зарна', 'Дугаар авсан', 'Дугаар аваагүй', '00 гүйлттэй',
]

const DOORS = ['', '3', '4', '5', '7']

const LEASING = ['', 'Лизингтэй', 'Лизинггүй']

const LOCATIONS = [
  '', 'Улаанбаатар', 'Дархан', 'Эрдэнэт', 'Чойбалсан',
  'Хан-Уул', 'Баянгол', 'Сүхбаатар', 'Чингэлтэй',
  'Баянзүрх', 'Сонгинохайрхан',
]

export default function SearchFilters({ filters, onChange, onReset }) {
  const [local, setLocal] = useState(filters)

  const update = (key, value) => {
    setLocal((prev) => ({ ...prev, [key]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onChange(local)
  }

  const handleReset = () => {
    const empty = {
      make: '', model: '', year_from: '', year_to: '',
      price_min: '', price_max: '', fuel: '',
      transmission: '', body_type: '', color: '',
      steering: '', drive_type: '', condition: '',
      doors: '', leasing: '', location: '',
    }
    setLocal(empty)
    onReset()
  }

  return (
    <aside className="filters-sidebar">
      <div className="filters-title">
        <SlidersHorizontal size={18} />
        Шүүлтүүр
      </div>
      <form onSubmit={handleSubmit}>
        <div className="filter-group">
          <label className="filter-label">Марк</label>
          <select className="filter-select" value={local.make} onChange={(e) => update('make', e.target.value)}>
            <option value="">Бүх марк</option>
            {MAKES.filter(Boolean).map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Модель</label>
          <input
            className="filter-input"
            type="text"
            placeholder="Жнь: Prius, Sonata..."
            value={local.model}
            onChange={(e) => update('model', e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label className="filter-label">Он</label>
          <div className="filter-row">
            <input
              className="filter-input"
              type="number"
              placeholder="Эхлэх"
              min="1990"
              max="2026"
              value={local.year_from}
              onChange={(e) => update('year_from', e.target.value)}
            />
            <input
              className="filter-input"
              type="number"
              placeholder="Дуусах"
              min="1990"
              max="2026"
              value={local.year_to}
              onChange={(e) => update('year_to', e.target.value)}
            />
          </div>
        </div>

        <div className="filter-group">
          <label className="filter-label">Үнэ (₮)</label>
          <div className="filter-row">
            <input
              className="filter-input"
              type="number"
              placeholder="Доод"
              step="100000"
              value={local.price_min}
              onChange={(e) => update('price_min', e.target.value)}
            />
            <input
              className="filter-input"
              type="number"
              placeholder="Дээд"
              step="100000"
              value={local.price_max}
              onChange={(e) => update('price_max', e.target.value)}
            />
          </div>
        </div>

        <div className="filter-group">
          <label className="filter-label">Түлшний төрөл</label>
          <select className="filter-select" value={local.fuel} onChange={(e) => update('fuel', e.target.value)}>
            {FUEL_TYPES.map((f) => (
              <option key={f} value={f}>{f || 'Бүх төрөл'}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Хурдны хайрцаг</label>
          <select className="filter-select" value={local.transmission} onChange={(e) => update('transmission', e.target.value)}>
            {TRANSMISSIONS.map((t) => (
              <option key={t} value={t}>{t || 'Бүх төрөл'}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Төрөл</label>
          <select className="filter-select" value={local.body_type} onChange={(e) => update('body_type', e.target.value)}>
            {BODY_TYPES.map((b) => (
              <option key={b} value={b}>{b || 'Бүх төрөл'}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Хүрд</label>
          <select className="filter-select" value={local.steering} onChange={(e) => update('steering', e.target.value)}>
            {STEERING.map((s) => (
              <option key={s} value={s}>{s || 'Бүх төрөл'}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Хөтлөгч</label>
          <select className="filter-select" value={local.drive_type} onChange={(e) => update('drive_type', e.target.value)}>
            {DRIVE_TYPES.map((d) => (
              <option key={d} value={d}>{d || 'Бүх төрөл'}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Өнгө</label>
          <select className="filter-select" value={local.color} onChange={(e) => update('color', e.target.value)}>
            {COLORS.map((c) => (
              <option key={c} value={c}>{c || 'Бүх өнгө'}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Нөхцөл</label>
          <select className="filter-select" value={local.condition} onChange={(e) => update('condition', e.target.value)}>
            {CONDITIONS.map((c) => (
              <option key={c} value={c}>{c || 'Бүх нөхцөл'}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Хаалга</label>
          <select className="filter-select" value={local.doors} onChange={(e) => update('doors', e.target.value)}>
            {DOORS.map((d) => (
              <option key={d} value={d}>{d || 'Бүх төрөл'}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Лизинг</label>
          <select className="filter-select" value={local.leasing} onChange={(e) => update('leasing', e.target.value)}>
            {LEASING.map((l) => (
              <option key={l} value={l}>{l || 'Бүх төрөл'}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Байршил</label>
          <select className="filter-select" value={local.location} onChange={(e) => update('location', e.target.value)}>
            {LOCATIONS.map((l) => (
              <option key={l} value={l}>{l || 'Бүх байршил'}</option>
            ))}
          </select>
        </div>

        <div className="filter-buttons">
          <button type="submit" className="btn btn-primary">Хайх</button>
          <button type="button" className="btn btn-secondary" onClick={handleReset}>Цэвэрлэх</button>
        </div>
      </form>
    </aside>
  )
}
