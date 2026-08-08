import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Link } from 'react-router-dom'
import { useAnalysis } from '../services/AnalysisContext'

const SENTIMENT_COLORS = {
  Positive: '#0f6b4c',
  Neutral: '#5c6570',
  Negative: '#9b2c2c',
}

const THEME_COLORS = [
  '#0f6b4c',
  '#1f6f8b',
  '#3b6d11',
  '#8a5a00',
  '#7a3e66',
  '#9b2c2c',
  '#35586e',
  '#4d6b3c',
  '#5c6570',
  '#2f4858',
]

export default function Dashboard() {
  const { uploadResult } = useAnalysis()

  if (!uploadResult?.stats) {
    return (
      <section className="panel">
        <h2>Dashboard</h2>
        <div className="empty-state">
          No analysis yet. <Link to="/upload">Upload a CSV</Link> to see
          statistics and charts.
        </div>
      </section>
    )
  }

  const stats = uploadResult.stats
  const sentimentData = Object.entries(stats.sentiment_distribution || {}).map(
    ([name, value]) => ({ name, value }),
  )
  const themeData = Object.entries(stats.theme_distribution || {}).map(
    ([name, value]) => ({ name, value }),
  )
  const ratingData = Object.entries(stats.rating_distribution || {})
    .map(([name, value]) => ({ name: `${name}★`, value }))
    .sort((a, b) => a.name.localeCompare(b.name))

  return (
    <section>
      <div className="panel">
        <h2>Dashboard</h2>
        <p className="subtitle">
          Statistics from the latest CSV analysis ({stats.total_reviews} reviews).
        </p>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total reviews</div>
            <div className="stat-value">{stats.total_reviews}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Positive</div>
            <div className="stat-value">{stats.positive_reviews}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Neutral</div>
            <div className="stat-value">{stats.neutral_reviews}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Negative</div>
            <div className="stat-value">{stats.negative_reviews}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Average rating</div>
            <div className="stat-value">
              {stats.average_rating != null ? stats.average_rating : '—'}
            </div>
          </div>
        </div>

        <div className="charts-grid">
          <div className="chart-panel">
            <h3>Sentiment Distribution</h3>
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {sentimentData.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={SENTIMENT_COLORS[entry.name] || '#888'}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-panel">
            <h3>Theme Distribution</h3>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={themeData} margin={{ bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d7e0da" />
                <XAxis
                  dataKey="name"
                  interval={0}
                  angle={-25}
                  textAnchor="end"
                  height={60}
                  tick={{ fontSize: 11 }}
                />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {themeData.map((entry, idx) => (
                    <Cell
                      key={entry.name}
                      fill={THEME_COLORS[idx % THEME_COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-panel">
            <h3>Rating Distribution</h3>
            {ratingData.length === 0 ? (
              <div className="empty-state">No rating column in this upload.</div>
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={ratingData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#d7e0da" />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#1f6f8b" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
