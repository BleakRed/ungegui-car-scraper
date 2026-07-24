import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function Pagination({ page, totalPages, onChange }) {
  if (totalPages <= 1) return null

  const getPages = () => {
    const pages = []
    const delta = 2
    const left = Math.max(2, page - delta)
    const right = Math.min(totalPages - 1, page + delta)

    pages.push(1)
    if (left > 2) pages.push('...')
    for (let i = left; i <= right; i++) pages.push(i)
    if (right < totalPages - 1) pages.push('...')
    if (totalPages > 1) pages.push(totalPages)

    return pages
  }

  return (
    <nav className="pagination">
      <button
        className="pagination-btn"
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
        aria-label="Өмнөх"
      >
        <ChevronLeft size={16} />
      </button>

      {getPages().map((p, i) =>
        p === '...' ? (
          <span key={`e${i}`} className="pagination-ellipsis">...</span>
        ) : (
          <button
            key={p}
            className={`pagination-btn${p === page ? ' active' : ''}`}
            onClick={() => onChange(p)}
          >
            {p}
          </button>
        )
      )}

      <button
        className="pagination-btn"
        disabled={page >= totalPages}
        onClick={() => onChange(page + 1)}
        aria-label="Дараа"
      >
        <ChevronRight size={16} />
      </button>
    </nav>
  )
}
