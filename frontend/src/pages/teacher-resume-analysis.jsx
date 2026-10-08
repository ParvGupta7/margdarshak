import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import UploadPage from './UploadPage.jsx'
import styles from '../components/AuthStyles.module.css'

/**
 * Extract and normalize skills from analysis response.
 * Returns all extracted skills for display.
 */
function getSkills(analysis) {
  const skills = analysis?.skills
  if (Array.isArray(skills)) return skills
  return skills?.matched_skills || skills?.found || []
}

/**
 * Extract TOP 5 skills from the complete skill list.
 * 
 * CRITICAL RULE: Only the first 5 skills (top_5) are stored for teacher matching.
 * This ensures only primary expertise is used when matching with students.
 * 
 * The ranking comes from the existing resume analysis pipeline,
 * which already scores and orders skills by relevance.
 */
function getTop5Skills(allSkills) {
  // Take only the first 5 skills for teacher's matching expertise
  return allSkills.slice(0, 5)
}

export default function TeacherResumeAnalysis() {
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState(null)
  const [savedTopSkills, setSavedTopSkills] = useState([])

  function handleAnalysisComplete(data) {
    const nextAnalysis = data?.analysis || data
    const allExtractedSkills = getSkills(nextAnalysis)
    const top5Skills = getTop5Skills(allExtractedSkills)
    
    // Store TOP 5 skills in localStorage for use in teacher dashboard
    localStorage.setItem('margdarshak_teacher_top_skills', JSON.stringify(top5Skills))
    setSavedTopSkills(top5Skills)
    
    setAnalysis(nextAnalysis)
  }

  if (analysis) {
    const allSkills = getSkills(analysis)
    const top5Skills = getTop5Skills(allSkills)
    const roles = analysis?.job_roles?.recommendations || analysis?.job_roles?.top_roles || []
    
    return (
      <div className={styles.dashboardShell}>
        {/* Header */}
        <header className={styles.dashboardTopBar}>
          <div className={styles.dashboardBrand}>
            <div className={styles.logoWrap}>M</div>
            <div>
              <div className={styles.dashboardTitle}>Teacher Portal</div>
              <div className={styles.dashboardSubtitle}>Resume Analysis</div>
            </div>
          </div>
          <button 
            type="button" 
            className={styles.logoutBtn} 
            onClick={() => navigate('/teacher/dashboard')}
          >
            Back to dashboard
          </button>
        </header>

        <main className={styles.teacherWorkspace}>
          {/* Success Message */}
          <section className={styles.teacherHero}>
            <span className={styles.dashboardSubtitle}>Analysis complete</span>
            <h1>Your teaching expertise profile</h1>
            <p>Your top 5 skills have been extracted and saved for student matching. Your complete skill profile is shown below for reference.</p>
          </section>

          {/* Content Grid */}
          <div className={styles.teacherGrid}>
            
            {/* Left Panel: All Extracted Skills */}
            <section className={styles.teacherPanelCard}>
              <span className={styles.dashboardSubtitle}>Complete skill analysis</span>
              <h2>{allSkills.length} Skills Found</h2>
              <p className={styles.teacherMuted}>
                These are all the skills extracted from your resume. Your TOP 5 are automatically selected for matching.
              </p>
              
              {allSkills.length > 0 ? (
                <div className={styles.expertiseList}>
                  {allSkills.map((skill, index) => (
                    <div key={skill} style={{ backgroundColor: index < 5 ? 'var(--bg-primary)' : 'rgba(255, 112, 72, 0.08)' }}>
                      <strong>
                        {index + 1}. {skill}
                        {index < 5 && <span style={{ marginLeft: '8px', color: 'var(--gold)', fontSize: '0.8em' }}>★ TOP 5</span>}
                      </strong>
                      <span>{index < 5 ? 'Primary expertise (matching)' : 'Supporting skill (reference only)'}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className={styles.teacherMuted}>No skills were detected. Try uploading a clearer resume.</p>
              )}
            </section>

            {/* Right Panel: Top 5 Expertise */}
            <section className={styles.teacherPanelCard}>
              <span className={styles.dashboardSubtitle}>Top 5 expertise</span>
              <h2>Your Matching Expertise</h2>
              <p className={styles.teacherMuted}>
                Only these 5 skills will be used to match you with students who need these competencies.
              </p>
              
              {top5Skills.length > 0 ? (
                <div className={styles.expertiseList}>
                  {top5Skills.map((skill, index) => (
                    <div key={skill}>
                      <strong>{index + 1}. {skill}</strong>
                      <span>Primary matching expertise</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className={styles.teacherMuted}>No TOP 5 skills available.</p>
              )}

              {/* Suggested Roles */}
              <h2 style={{ marginTop: '28px' }}>Career Direction</h2>
              {roles.length > 0 ? (
                <ul>
                  {roles.slice(0, 5).map(role => (
                    <li key={role.role || role.name}>{role.role || role.name}</li>
                  ))}
                </ul>
              ) : (
                <p className={styles.teacherMuted}>
                  Role suggestions are available in the full analysis response.
                </p>
              )}

              {/* Action Button */}
              <button 
                type="button" 
                className={styles.submitBtn}
                style={{ marginTop: '20px' }}
                onClick={() => navigate('/teacher/dashboard')}
              >
                Go to Dashboard
              </button>
            </section>
          </div>

          {/* Information Banner */}
          <section style={{ marginTop: '48px', padding: '20px', background: 'var(--bg-card)', border: '1px solid var(--border)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <strong>Important:</strong> Your TOP 5 skills have been saved and will be used to find students who need help with these specific competencies. Skills ranked 6th and beyond are displayed for your reference but are not used for matching. This ensures focus on your core expertise.
          </section>

          {/* Re-analyze Button */}
          <div style={{ textAlign: 'center', marginTop: '32px' }}>
            <button 
              type="button" 
              className={styles.demoBtn}
              onClick={() => setAnalysis(null)}
            >
              Analyze another resume
            </button>
          </div>
        </main>
      </div>
    )
  }

  // Upload state
  return (
    <div className={styles.dashboardShell}>
      <header className={styles.dashboardTopBar}>
        <div className={styles.dashboardBrand}>
          <div className={styles.logoWrap}>M</div>
          <div>
            <div className={styles.dashboardTitle}>Teacher Portal</div>
            <div className={styles.dashboardSubtitle}>Analyze your teaching expertise</div>
          </div>
        </div>
        <button 
          type="button" 
          className={styles.logoutBtn} 
          onClick={() => navigate('/teacher/dashboard')}
        >
          Back to dashboard
        </button>
      </header>
      <UploadPage compact onAnalysisComplete={handleAnalysisComplete} />
    </div>
  )
}
