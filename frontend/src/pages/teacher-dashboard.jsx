import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { recommendStudentsForTeacher } from '../utils/api.js'
import { supabase } from '../lib/supabaseClient.js'
import styles from '../components/AuthStyles.module.css'

/**
 * DEMO_TEACHER: Harshita
 * 
 * This is a seeded demo profile demonstrating the Teacher Module.
 * Her TOP 5 skills are extracted from the resume analysis pipeline.
 * 
 * Top 5 Expertise (used for student-teacher matching):
 * 1. React
 * 2. JavaScript
 * 3. TypeScript
 * 4. Python
 * 5. Machine Learning
 * 
 * CRITICAL: Only these 5 skills are used for matching against student requirements.
 * Skills beyond the top 5 are NOT considered for recommendations.
 */
const DEMO_TEACHER = {
  id: 'teacher_harshita',
  name: 'Harshita',
  email: 'teacher.demo@margdarshak.local',
  headline: 'Frontend Engineering & React Mentor',
  bio: 'Frontend engineer mentoring learners through practical React projects and modern web development.',
  
  // Top 5 expertise (primary matching criteria)
  top_5_expertise: ['React', 'JavaScript', 'TypeScript', 'Python', 'Machine Learning'],
  
  // Supporting professional information (not used for matching)
  projects: ['React dashboard platform', 'React portfolio builder', 'ML skills tracker'],
  experience_years: 5,
  teaching_experience_years: 3,
  rating: 4.8,
  sessions_completed: 120,
}

/**
 * Retrieve teacher's TOP 5 skills from localStorage (set during resume analysis).
 * Falls back to DEMO_TEACHER profile if not found.
 * 
 * CRITICAL RULE: Only TOP 5 skills are returned, never more.
 * This ensures matching only uses primary expertise.
 */
function getStoredTopSkills() {
  try {
    const stored = JSON.parse(localStorage.getItem('margdarshak_teacher_top_skills') || '[]')
    // Strict: ensure array and slice to exactly 5
    if (Array.isArray(stored) && stored.length > 0) {
      return stored.slice(0, 5)
    }
  } catch {
    // Silent fallback on JSON parse error
  }
  // Fallback to demo top 5
  return DEMO_TEACHER.top_5_expertise
}

export default function TeacherDashboard() {
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [topSkills, setTopSkills] = useState([])

  useEffect(() => {
    const initializeDashboard = async () => {
      setLoading(true)
      
      // Get teacher's top 5 skills
      const selectedSkills = getStoredTopSkills()
      setTopSkills(selectedSkills)
      
      // Check auth session
      try {
        const { data } = await supabase.auth.getSession()
        setSession(data.session)
      } catch {
        // Auth check failed, but demo mode can continue
      }
      
      // Fetch students whose requirements match teacher's TOP 5 expertise
      try {
        const data = await recommendStudentsForTeacher(DEMO_TEACHER.id, selectedSkills)
        setStudents(data.recommendations || [])
        setError('')
      } catch (err) {
        const errorMsg = err.response?.data?.detail || err.message || 'Could not load student matches.'
        setError(errorMsg)
      }
      
      setLoading(false)
    }
    
    initializeDashboard()
  }, [])

  async function handleLogout() {
    localStorage.removeItem('margdarshak_teacher_demo')
    localStorage.removeItem('margdarshak_teacher_top_skills')
    await supabase.auth.signOut()
    navigate('/teacher-login', { replace: true })
  }

  const isDemo = localStorage.getItem('margdarshak_teacher_demo') === 'true'

  return (
    <div className={styles.dashboardShell}>
      {/* Top Navigation Bar */}
      <header className={styles.dashboardTopBar}>
        <div className={styles.dashboardBrand}>
          <div className={styles.logoWrap}>M</div>
          <div>
            <div className={styles.dashboardTitle}>Teacher Portal</div>
            <div className={styles.dashboardSubtitle}>Professional Mentor Workspace</div>
          </div>
        </div>
        
        <div className={styles.dashboardUserBlock}>
          <span className={styles.dashboardUserLabel}>
            {isDemo ? 'Demo teacher' : 'Signed in as teacher'}
          </span>
          <span className={styles.dashboardUserValue}>
            {isDemo ? DEMO_TEACHER.email : (session?.user?.email || 'Teacher')}
          </span>
        </div>
        
        <button type="button" className={styles.logoutBtn} onClick={handleLogout}>
          Logout
        </button>
      </header>

      <main className={styles.teacherWorkspace}>
        {/* Hero Section */}
        <section className={styles.teacherHero}>
          <span className={styles.dashboardSubtitle}>Professional expertise dashboard</span>
          <h1>Welcome, {DEMO_TEACHER.name}</h1>
          <p>{DEMO_TEACHER.headline}</p>
          <button 
            type="button" 
            className={styles.submitBtn} 
            onClick={() => navigate('/teacher/analyze')}
          >
            Analyze my resume
          </button>
        </section>

        {/* Stats Overview */}
        <section className={styles.teacherStats}>
          <div>
            <strong>{topSkills.length}</strong>
            <span>Top expertise</span>
          </div>
          <div>
            <strong>{DEMO_TEACHER.projects.length}</strong>
            <span>Projects</span>
          </div>
          <div>
            <strong>{students.length}</strong>
            <span>Students matched</span>
          </div>
          <div>
            <strong>{DEMO_TEACHER.teaching_experience_years} yrs</strong>
            <span>Teaching</span>
          </div>
        </section>

        {/* Main Content Grid */}
        <div className={styles.teacherGrid}>
          
          {/* Left Panel: Top 5 Expertise */}
          <section className={styles.teacherPanelCard}>
            <span className={styles.dashboardSubtitle}>Professional expertise</span>
            <h2>Top 5 Skills</h2>
            
            {topSkills.length > 0 ? (
              <div className={styles.expertiseList}>
                {topSkills.map((skill, index) => (
                  <div key={skill}>
                    <strong>{index + 1}. {skill}</strong>
                    <span>Primary expertise</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className={styles.teacherMuted}>
                No skills loaded. Analyze your resume to populate your expertise.
              </p>
            )}
            
            <h2 style={{ marginTop: '28px' }}>Professional Experience</h2>
            <div className={styles.expertiseList}>
              <div>
                <strong>{DEMO_TEACHER.experience_years} years</strong>
                <span>Industry experience</span>
              </div>
              <div>
                <strong>{DEMO_TEACHER.teaching_experience_years} years</strong>
                <span>Teaching experience</span>
              </div>
              <div>
                <strong>{DEMO_TEACHER.rating}/5.0</strong>
                <span>Student rating</span>
              </div>
              <div>
                <strong>{DEMO_TEACHER.sessions_completed}</strong>
                <span>Sessions completed</span>
              </div>
            </div>
            
            <h2 style={{ marginTop: '28px' }}>Projects</h2>
            {DEMO_TEACHER.projects.length > 0 ? (
              <ul>
                {DEMO_TEACHER.projects.map(project => (
                  <li key={project}>{project}</li>
                ))}
              </ul>
            ) : (
              <p className={styles.teacherMuted}>No projects listed.</p>
            )}
          </section>

          {/* Right Panel: Matched Students */}
          <section className={styles.teacherPanelCard}>
            <span className={styles.dashboardSubtitle}>Student matching</span>
            <h2>Students You Can Help</h2>
            <p className={styles.teacherMuted}>
              Students whose skill requirements match your top 5 expertise areas.
            </p>

            {/* Loading State */}
            {loading && (
              <div className={styles.studentMatchList}>
                <p className={styles.teacherMuted}>Loading student matches...</p>
              </div>
            )}

            {/* Error State */}
            {error && !loading && (
              <div style={{ padding: '16px', background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--error)', marginTop: '16px' }}>
                <p>{error}</p>
              </div>
            )}

            {/* No Match State */}
            {!loading && !error && students.length === 0 && (
              <div className={styles.studentMatchList}>
                <p className={styles.teacherMuted}>
                  No matching students found at this time. Students with requirements that align with your top 5 expertise will appear here.
                </p>
              </div>
            )}

            {/* Students List */}
            {!loading && students.length > 0 && (
              <div className={styles.studentMatchList}>
                {students.map(match => (
                  <article key={match.student.id} className={styles.studentMatch}>
                    {/* Student Header with Match Score */}
                    <div className={styles.studentMatchHeader}>
                      <div>
                        <strong>{match.student.name}</strong>
                        <span>
                          {match.matched_skills.length > 0
                            ? `Matched skills: ${match.matched_skills.join(', ')}`
                            : 'No matched skills'}
                        </span>
                      </div>
                      <b>{Math.round(match.match_score)}%</b>
                    </div>

                    {/* Student Profile Description */}
                    <p>{match.student.profile}</p>

                    {/* Evidence/Reasoning */}
                    {match.evidence.length > 0 && (
                      <div className={styles.evidenceList}>
                        {match.evidence.map(item => (
                          <span key={item}>✓ {item}</span>
                        ))}
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className={styles.teacherActions}>
                      <button type="button" className={styles.submitBtn}>
                        View profile
                      </button>
                      <button type="button" className={styles.logoutBtn}>
                        Connect
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Methodology Note */}
        <section style={{ marginTop: '48px', padding: '20px', background: 'var(--bg-card)', border: '1px solid var(--border)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <strong>Matching Methodology:</strong> Students are recommended when their required skills match your TOP 5 expertise areas. Only your top 5 skills are used for matching to ensure focus on your core competencies. Skills beyond the top 5 are not considered for recommendations.
        </section>
      </main>
    </div>
  )
}
