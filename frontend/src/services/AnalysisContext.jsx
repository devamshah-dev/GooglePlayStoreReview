import { createContext, useContext, useMemo, useState } from 'react'

const AnalysisContext = createContext(null)

export function AnalysisProvider({ children }) {
  const [uploadResult, setUploadResult] = useState(null)

  const value = useMemo(
    () => ({
      uploadResult,
      setUploadResult,
      clearUploadResult: () => setUploadResult(null),
    }),
    [uploadResult],
  )

  return (
    <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>
  )
}

export function useAnalysis() {
  const ctx = useContext(AnalysisContext)
  if (!ctx) {
    throw new Error('useAnalysis must be used within AnalysisProvider')
  }
  return ctx
}
