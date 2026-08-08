import { useState } from 'react'
import { Link } from 'react-router-dom'
import { getErrorMessage, uploadCsv } from '../services/api'
import { useAnalysis } from '../services/AnalysisContext'

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

export default function Upload() {
  const { setUploadResult, uploadResult } = useAnalysis()
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function handleUpload(e) {
    e.preventDefault()
    setError('')
    setMessage('')

    if (!file) {
      setError('Please select a CSV file to upload.')
      return
    }
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Invalid file type. Please upload a .csv file.')
      return
    }

    setLoading(true)
    try {
      const data = await uploadCsv(file)
      setUploadResult(data)
      setMessage(data.message || 'Analysis complete.')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel">
      <h2>Upload CSV</h2>
      <p className="subtitle">
        Upload a Google Play reviews CSV. The backend detects common review/rating
        column names, predicts sentiment and theme, and returns downloadable results.
      </p>

      <form onSubmit={handleUpload}>
        <input
          className="file-input"
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          disabled={loading}
        />
        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner" /> Analyzing reviews...
              </>
            ) : (
              'Upload & Analyze'
            )}
          </button>
          {uploadResult?.csv_data && (
            <button
              className="btn btn-secondary"
              type="button"
              onClick={() => downloadCsv(uploadResult.csv_data)}
            >
              Download Results CSV
            </button>
          )}
        </div>
      </form>

      {error && <div className="alert alert-error">{error}</div>}
      {message && <div className="alert alert-success">{message}</div>}

      {uploadResult && (
        <div className="alert alert-info" style={{ marginTop: '1rem' }}>
          Analyzed <strong>{uploadResult.total_rows}</strong> reviews.{' '}
          <Link to="/dashboard">View dashboard</Link> ·{' '}
          <Link to="/results">View results table</Link>
        </div>
      )}
    </section>
  )
}
