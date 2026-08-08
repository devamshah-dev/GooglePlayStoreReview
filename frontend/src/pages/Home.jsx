import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <section>
      <div className="hero">
        <h1>Google Play Review Classification Platform</h1>
        <p>
          Analyze Play Store reviews with classical machine learning. Predict
          sentiment and complaint themes from review text using TF-IDF and
          lightweight classifiers — no GPU required.
        </p>
        <div className="hero-actions">
          <Link className="btn btn-primary" to="/analyze">
            Analyze a Review
          </Link>
          <Link className="btn btn-secondary" to="/upload">
            Upload CSV
          </Link>
        </div>
      </div>

      <div className="feature-list">
        <article className="feature-item">
          <h3>Single review</h3>
          <p>Paste one review and get sentiment plus theme instantly.</p>
        </article>
        <article className="feature-item">
          <h3>Batch CSV</h3>
          <p>Upload a reviews CSV, run predictions, and download results.</p>
        </article>
        <article className="feature-item">
          <h3>Dashboard</h3>
          <p>See sentiment, theme, and rating distributions after analysis.</p>
        </article>
      </div>
    </section>
  )
}
