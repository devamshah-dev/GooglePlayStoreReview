import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAnalysis } from '../services/AnalysisContext'

const PAGE_SIZE = 10

function sentimentPill(sentiment) {
  const s = (sentiment || '').toLowerCase()
  if (s === 'positive') return 'pill pill-positive'
  if (s === 'negative') return 'pill pill-negative'
  return 'pill pill-neutral'
}

function downloadCsv(csvData, filename = 'predicted_reviews.csv') {
  const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function Results() {
  const { uploadResult } = useAnalysis()
  const [page, setPage] = useState(0)

  const rows = uploadResult?.results || []
  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE))

  const pageRows = useMemo(() => {
    const start = page * PAGE_SIZE
    return rows.slice(start, start + PAGE_SIZE)
  }, [rows, page])

  if (!uploadResult) {
    return (
      <section className="panel">
        <h2>Results</h2>
        <div className="empty-state">
          No results yet. <Link to="/upload">Upload a CSV</Link> first.
        </div>
      </section>
    )
  }

  return (
    <section className="panel">
      <h2>Results</h2>
      <p className="subtitle">
        Showing up to {rows.length} preview rows
        {uploadResult.total_rows > rows.length
          ? ` (of ${uploadResult.total_rows} total — download CSV for the full set)`
          : ''}
        .
      </p>

      <div className="form-actions" style={{ marginTop: 0, marginBottom: '0.9rem' }}>
        <button
          className="btn btn-primary"
          type="button"
          onClick={() => downloadCsv(uploadResult.csv_data)}
        >
          Download Results CSV
        </button>
        <Link className="btn btn-secondary" to="/dashboard">
          Open Dashboard
        </Link>
      </div>

      <div className="table-wrap">
        <table className="results-table">
          <thead>
            <tr>
              <th>Review</th>
              <th>Rating</th>
              <th>Sentiment</th>
              <th>Theme</th>
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, idx) => (
              <tr key={`${page}-${idx}`}>
                <td className="review-cell">{row.review}</td>
                <td>{row.rating ?? '—'}</td>
                <td>
                  <span className={sentimentPill(row.predicted_sentiment)}>
                    {row.predicted_sentiment}
                  </span>
                </td>
                <td>
                  <span className="pill pill-theme">{row.predicted_theme}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button
          className="btn btn-secondary"
          type="button"
          disabled={page <= 0}
          onClick={() => setPage((p) => Math.max(0, p - 1))}
        >
          Previous
        </button>
        <span>
          Page {page + 1} of {totalPages}
        </span>
        <button
          className="btn btn-secondary"
          type="button"
          disabled={page >= totalPages - 1}
          onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
        >
          Next
        </button>
      </div>
    </section>
  )
}
