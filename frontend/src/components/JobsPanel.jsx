import { useState } from 'react'
import { fetchJobs } from '../utils/api.js'
import styles from './JobsPanel.module.css'

export default function JobsPanel({ jobs: initialJobs, analysis }) {
  const [jobs, setJobs] = useState(initialJobs)
  const [searchRole, setSearchRole] = useState(analysis?.job_roles?.best_match?.role || '')
  const [searchLocation, setSearchLocation] = useState(analysis?.entities?.location || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const topRoles = analysis?.job_roles?.top_roles || []

  async function handleSearch() {
    if (!searchRole) return
    setLoading(true)
    setError(null)
    try {
      const data = await fetchJobs(searchRole, searchLocation)
      setJobs(data)
    } catch (err) {
      setError('Failed to fetch jobs. Check your connection.')
    } finally {
      setLoading(false)
    }
  }

  const jobList = jobs?.jobs || []

  return (
    <div className={styles.container + ' stagger'}>
      {/* Search controls */}
      <div className={styles.searchCard}>
        <h3 className={styles.searchTitle}>Search live job listings</h3>
        <div className={styles.searchRow}>
          <div className={styles.searchField}>
            <label className={styles.fieldLabel}>Job Role</label>
            <div className={styles.inputRow}>
              <input
                className={styles.input}
                value={searchRole}
                onChange={e => setSearchRole(e.target.value)}
                placeholder="e.g. Data Scientist"
              />
              <div className={styles.quickRoles}>
                {topRoles.slice(0, 3).map(role => (
                  <button
                    key={role.role}
                    className={`${styles.quickBtn} ${searchRole === role.role ? styles.quickBtnActive : ''}`}
                    onClick={() => setSearchRole(role.role)}
                  >
                    {role.role}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className={styles.searchField}>
            <label className={styles.fieldLabel}>Location</label>
            <input
              className={styles.input}
              value={searchLocation}
              onChange={e => setSearchLocation(e.target.value)}
              placeholder="e.g. Bangalore, Mumbai"
            />
          </div>

          <button
            className={styles.searchBtn}
            onClick={handleSearch}
            disabled={loading || !searchRole}
          >
            {loading ? <span className="spinner" /> : 'Search Jobs'}
          </button>
        </div>
      </div>

      {error && <div className={styles.errorBanner}>{error}</div>}

      {/* Status bar */}
      {jobs && (
        <div className={styles.statusBar}>
          {jobs.status === 'mock' ? (
            <span className={styles.mockNote}>
              Add Adzuna API keys to .env to see real listings. Showing placeholder.
            </span>
          ) : (
            <span className={styles.resultCount}>
              {jobs.total_found} jobs found for "{jobs.query?.role}" in {jobs.query?.location}
            </span>
          )}
        </div>
      )}

      {/* Job listings */}
      {jobList.length === 0 ? (
        <div className={styles.empty}>No job listings found. Try a different role or location.</div>
      ) : (
        <div className={styles.jobList}>
          {jobList.map((job, i) => (
            <a
              key={i}
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.jobCard}
            >
              <div className={styles.jobHeader}>
                <div>
                  <h3 className={styles.jobTitle}>{job.title}</h3>
                  <span className={styles.jobCompany}>{job.company}</span>
                </div>
                <div className={styles.jobMeta}>
                  {job.salary && job.salary !== 'Not disclosed' && (
                    <span className={styles.jobSalary}>{job.salary}</span>
                  )}
                  <span className={styles.jobLocation}>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                      <circle cx="12" cy="10" r="3"/>
                    </svg>
                    {job.location}
                  </span>
                </div>
              </div>
              {job.description && (
                <p className={styles.jobDesc}>{job.description}</p>
              )}
              <div className={styles.jobFooter}>
                <span className={styles.jobDate}>{job.created}</span>
                <span className={styles.applyLink}>
                  View & Apply
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                  </svg>
                </span>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
