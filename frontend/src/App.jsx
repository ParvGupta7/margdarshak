import { useState } from 'react'
import UploadPage from './pages/UploadPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import Chatbot from './components/Chatbot.jsx'

export default function App() {
  const [analysis, setAnalysis] = useState(null)
  const [activeTab, setActiveTab] = useState('profile')

  function handleAnalysisComplete(data) {
    setAnalysis(data)
    setActiveTab('profile')
  }

  function handleReset() {
    setAnalysis(null)
  }

  return (
    <>
      {!analysis ? (
        <UploadPage onAnalysisComplete={handleAnalysisComplete} />
      ) : (
        <DashboardPage
          analysis={analysis}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onReset={handleReset}
        />
      )}

      {/* Chatbot is visible on dashboard only */}
      {analysis && <Chatbot analysis={analysis} />}
    </>
  )
}
