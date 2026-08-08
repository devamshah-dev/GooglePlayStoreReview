import { useState } from 'react'
import { getErrorMessage, predictReview } from '../services/api'

function sentimentClass(sentiment) {
  const s = (sentiment || '').toLowerCase()
  if (s === 'positive') return 'positive'
  if (s === 'negative') return 'negative'
  return 'neutral'
}

export default function Analyze() {
  const [review, setReview] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function handleAnalyze(e) {
    e.preventDefault()
    setError('')
    setResult(null)

    const text = review.trim()
    if (!text) {
      setError('Please enter a review before analyzing.')
      return
    }

    setLoading(true)
    try {
      const data = await predictReview(text)
      setResult(data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel">
      <h2>Analyze Review</h2>
      <p className="subtitle">
        Enter a Google Play Store review. Predictions come from trained TF-IDF
        classifiers (sentiment + theme).
      </p>

      <form onSubmit={handleAnalyze}>
        <textarea
          className="textarea"
          placeholder="Enter a Google Play Store review..."
          value={review}
          onChange={(e) => setReview(e.target.value)}
          disabled={loading}
        />
        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner" /> Analyzing...
              </>
            ) : (
              'Analyze Review'
            )}
          </button>
        </div>
      </form>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div>
          <div className="badge-row">
            <div className={`badge ${sentimentClass(result.sentiment)}`}>
              <div className="label">Sentiment</div>
              <div className="value">{(result.sentiment || '').toUpperCase()}</div>
            </div>
            <div className="badge theme">
              <div className="label">Theme</div>
              <div className="value">{(result.theme || '').toUpperCase()}</div>
            </div>
          </div>
          <div className="panel" style={{ marginTop: '1rem', boxShadow: 'none' }}>
            <div className="label" style={{ color: 'var(--ink-soft)', marginBottom: 6 }}>
              Original review
            </div>
            <p style={{ margin: 0, lineHeight: 1.5 }}>{result.review}</p>
          </div>
        </div>
      )}
    </section>
  )
}
